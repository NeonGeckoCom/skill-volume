# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Authors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import subprocess

from os.path import isfile, join
from adapt.intent import IntentBuilder
from mycroft_bus_client import Message
from neon_utils.message_utils import request_from_mobile
from neon_utils.skills.neon_skill import NeonSkill, LOG
from ovos_utils import resolve_resource_file

from mycroft.audio import wait_while_speaking
from mycroft.skills.core import intent_handler


class VolumeSkill(NeonSkill):

    MIN_LEVEL = 0
    MAX_LEVEL = 100

    # TODO: Translation layer (have to match word in Level.voc)
    VOLUME_WORDS = {
        'loud': 9,
        'normal': 6,
        'quiet': 3
    }

    def __init__(self):
        super(VolumeSkill, self).__init__("VolumeSkill")
        self.settings["default_level"] = 60  # can be 0 (off) to 100 (max)
        self.default_level = self.settings.get("default_level", 60)
        self.settings["min_volume"] = 0     # can be 0 to 100
        if self.config_core['enclosure'].get('platform') == 'mycroft_mark_1':
            self.settings["max_volume"] = 83   # can be 0 to 83
        else:
            self.settings["max_volume"] = 100   # can be 0 to 100
        self.volume_sound = join(dirname(__file__), "blop-mark-diangelo.wav")
        self.vol_before_mute = None
        self._mixer = None

        try:
            self.default_level = self.local_config["devVars"]["defaultMicVolume"]
        except KeyError:
            self.default_level = 100
            # self.create_signal("NGI_YAML_config_update")
            self.local_config.update_yaml_file("devVars", "defaultMicVolume", self.default_level)

        self.min_volume = 0
        self.max_volume = 100
        # self.mic_options = ["mic", "microphone", "input"]

        # TODO: Depreciate mic/vol levels and use API
        # Populate current volume levels
        if not self.server and isfile(join(self.local_config["dirVars"].get("ngiDir", ""), "functions.sh")):
            try:
                subprocess.call(['bash', '-c', ". " + self.local_config["dirVars"]["ngiDir"]
                                 + "/functions.sh; getLevel"])
                self.mic_level = int(open(self.local_config["dirVars"]["tempDir"] + "/input_volume").read())
                self.vol_level = int(open(self.local_config["dirVars"]["tempDir"] + "/output_volume").read())
            except Exception as e:
                LOG.error(e)
                self.mic_level = 0
                self.vol_level = 0
        else:
            self.mic_level = 0
            self.vol_level = 0

    def initialize(self):
        intent = IntentBuilder("IncreaseVolume").require("Volume").optionally("Mic").require("Increase").build()
        self.register_intent(intent, self.handle_increase_volume)

        intent = IntentBuilder("DecreaseVolume").require("Volume").optionally("Mic").require("Decrease").build()
        self.register_intent(intent, self.handle_decrease_volume)

        intent = IntentBuilder("MuteVolume").require("Mute").require("Volume").optionally("Mic").\
            optionally("time").build()
        self.register_intent(intent, self.handle_mute_volume)

        intent = IntentBuilder("UnmuteVolume").require("Volume").optionally("Mic").require("Unmute").build()
        self.register_intent(intent, self.handle_unmute_volume)

        if not self.server:
            self.bus.once("mycroft.ready", self._unmute_on_loaded)

    def _unmute_on_loaded(self, message):
        # TODO: Notify should probably go in a different skill DM
        from mycroft.util import play_wav
        notify_file = resolve_resource_file(self.local_config["fileVars"]["notify"])
        if notify_file:
            play_wav(notify_file)
        self.set_volume(io='input', setting=-1, speak=False)

    # Queries current volume and imports as mic_level and vol_level
    def _get_volume(self):
        """
        Populates self.mic_level and self.vol_level with current OS values
        """
        enclosure = self.local_config.get("devVars", {}).get("devType") or "generic"
        if enclosure in ("generic", "neonK", "neonX", "neonAlpha", "neonU") and\
                isfile(join(self.local_config["dirVars"].get("ngiDir", ""), "functions.sh")):
            subprocess.call(['bash', '-c', ". " + self.local_config["dirVars"]["ngiDir"]
                            + "/functions.sh; getLevel; exit"])
            LOG.debug("Volume Updated")
            self.mic_level = int(open(self.local_config["dirVars"]["tempDir"] + "/input_volume").read())
            self.vol_level = int(open(self.local_config["dirVars"]["tempDir"] + "/output_volume").read())
        else:
            self.mic_level = 100
            vol_response = self.bus.wait_for_response(Message("mycroft.volume.get"))
            if not vol_response:
                raise Exception("No response from enclosure module!")
            vol_percent = vol_response.data.get("percent")
            if isinstance(vol_percent, int):
                self.vol_level = vol_percent
            elif isinstance(vol_percent, float):
                self.vol_level = round(100 * vol_percent)
            else:
                LOG.error(vol_response)
                self.vol_level = 0

    def set_volume(self, io: str, setting, speak: bool = True):
        """
        Sets level of io to setting
        :param io: "input" or "output"
        :param setting: (0-100) (-1 for unmute)
        :param speak: boolean to speak confirmation of volume change
        """
        enclosure = self.local_config.get("devVars", {}).get("devType") or "generic"
        if enclosure in ("generic", "neonK", "neonX", "neonAlpha", "neonU") and\
                isfile(join(self.local_config["dirVars"].get("ngiDir", ""), "functions.sh")):
            subprocess.Popen(['bash', '-c', ". " + self.local_config["dirVars"]["ngiDir"]
                              + "/functions.sh; setLevel " + str(io) + " " + str(setting)])
        else:
            if str(io) == "input":
                LOG.warning(f"Input controls not implemented!")
            else:
                if str(setting) == '0':
                    self.bus.emit(Message("mycroft.volume.mute", {"mute": True}, {"origin": "volume.neon"}))
                elif str(setting) == '-1':
                    self.bus.emit(Message("mycroft.volume.mute", {"mute": False}, {"origin": "volume.neon"}))
                else:
                    self.bus.emit(Message("mycroft.volume.set", {"percent": setting/100}, {"origin": "volume.neon"}))
        if str(setting) == '0':
            if str(io) == 'input':
                pass
                # self.speak("Microphone muted.")
        elif str(setting) == '-1':
            if str(io) == 'output':
                kind = "Volume"
                volume = str(self.vol_level)
                # self.speak("Volume restored to " + str(self.vol_level) + ".", private=True)
            else:
                kind = "Microphone level"
                volume = self.mic_level
                # self.speak("Microphone restored to " + str(self.mic_level) + ".", private=True)
            if speak:
                self.speak_dialog("reset.volume", {"kind": kind, "volume": volume}, private=True)
        else:
            if str(io) == 'output':
                kind = "Volume"
                # self.speak("Volume set to " + str(setting) + " percent.", private=True)
            else:
                kind = "Microphone Level"
                # self.speak("Microphone level set to " + str(setting) + " percent.", private=True)
            if speak:
                self.speak_dialog("set.volume", {"kind": kind, "volume": str(setting)}, private=True)

    @intent_handler(IntentBuilder("SetVolume").optionally("Set").require("Volume").require("Level"))
    def handle_set_volume(self, message):
        level = self.extract_spoken_volume_level(message, self._get_volume())
        # LOG.info("Set Volume Intent")

        if request_from_mobile(message):
            # self.speak("MOBILE-INTENT VOLUME&level=" + str(level))
            self.mobile_skill_intent("volume", {"level": level}, message)
            # self.socket_io_emit('volume', f"&level={level}", message.context["flac_filename"])
        elif self.server:
            self.socket_emit_to_server("audio control", ["volume", level, message.context["klat_data"]["request_id"]])
            # self.socket_io_emit(event="audio control", kind="volume", message=level,
            #                     flac_filename=message.context["flac_filename"])
        else:
            if message.data.get("Mic"):
                self.set_volume(io='input', setting=level)
                # LOG.info("in mic")
            else:
                self.set_volume(io='output', setting=level)
        # if not self.check_for_signal("use_default_response", -1):
        #     self.speak_dialog('set.volume', data={'volume': level})
        # else:
        #     self.speak("Volume changed to {}".format(level))

    @intent_handler(IntentBuilder("QueryVolume").require("Volume").require("Query"))
    def handle_query_volume(self, message):
        if request_from_mobile(message):
            # self.speak("MOBILE-INTENT VOLUME&query")
            self.mobile_skill_intent("volume", {"query": ""}, message)
            # self.socket_io_emit('volume', 'query', message.context["flac_filename"])
        elif self.server:
            self.socket_emit_to_server("audio control", ["volume", "query", message.context["klat_data"]["request_id"]])
            # self.socket_io_emit(event="audio control", kind="volume", message="query",
            #                     flac_filename=message.context["flac_filename"])
        else:
            self._get_volume()
            if message.data.get("Mic"):
                level = self.mic_level
                self.speak_dialog('volume.is', data={'kind': 'microphone', 'volume': level}, private=True)
            else:
                level = self.vol_level
                if not self.check_for_signal("SKILLS_useDefaultResponses", -1):
                    self.speak_dialog('volume.is', data={'kind': 'volume', 'volume': level}, private=True)
                else:
                    self.speak("The volume is at {} percent.".format(level), private=True)

    def handle_increase_volume(self, message):
        if request_from_mobile(message):
            # self.speak("MOBILE-INTENT VOLUME&level=increase")
            self.speak("Increasing volume.", private=True)
            self.mobile_skill_intent("volume", {"level": "increase"}, message)
            # self.socket_io_emit('volume', '&level=increase', message.context["flac_filename"])
        elif self.server:
            self.socket_emit_to_server("audio control", ["volume", "increase",
                                                         message.context["klat_data"]["request_id"]])
            # self.socket_io_emit(event="audio control", kind="volume", message="increase",
            #                     flac_filename=message.context["flac_filename"])
        else:
            if message.data.get("Mic"):
                self.update_mic_volume(10)
                # LOG.info("in mic")
            else:
                self.update_volume(10)

    def stop(self):
        pass

    def handle_decrease_volume(self, message):
        if request_from_mobile(message):
            # self.speak("MOBILE-INTENT VOLUME&level=decrease")
            self.speak("Decreasing volume.", private=True)
            self.mobile_skill_intent("volume", {"level": "decrease"}, message)
            # self.socket_io_emit('volume', '&level=decrease', message.context["flac_filename"])
        elif self.server:
            self.socket_emit_to_server("audio control", ["volume", "decrease",
                                                         message.context["klat_data"]["request_id"]])
            # self.socket_io_emit(event="audio control", kind="volume", message="decrease",
            #                     flac_filename=message.context["flac_filename"])
        else:
            if message.data.get("Mic"):
                self.update_mic_volume(-10)
                # LOG.info("in mic")
            # Output
            else:
                self.update_volume(-10)

    def handle_mute_volume(self, message):
        if message.data.get("Mic"):
            if request_from_mobile(message):
                self.mobile_skill_intent("volume", {"state": "mute"}, message)
                # self.socket_io_emit('microphone', '&state=mute', message.context["flac_filename"])
            elif self.server:
                self.socket_emit_to_server("audio control",
                                           ["microphone", False, message.context["klat_data"]["request_id"]])
                # self.socket_io_emit(event="audio control", kind="microphone", message=False,
                #                     flac_filename=message.context["flac_filename"])
            else:
                self.set_volume(io='input', setting=0)
            self.speak_dialog('mute.volume', {"kind": "Microphone"}, private=True)
        else:
            speak_message = message.data.get('speak_message', True)
            if speak_message:
                # if not self.check_for_signal("use_default_response", -1):
                self.speak_dialog('mute.volume', {"kind": "Audio"}, private=True)
                # else:
                #     self.speak("Audio is going to be muted.", private=True)
                wait_while_speaking()
            if request_from_mobile(message):
                pass
            elif self.server:
                self.socket_emit_to_server("audio control",
                                           ["speech", False, message.context["klat_data"]["request_id"]])
                # self.socket_io_emit(event="audio control", kind="speech", message=False,
                #                     flac_filename=message.context["flac_filename"])
            else:
                self.set_volume(io='output', setting=0)

        # if message.data.get("mobile"):
        #     # self.speak("MOBILE-INTENT VOLUME&level=mute")
        #     if message.data.get("Mic") or self.mic_options[0] in message.data.get("utterance") \
        #             or self.mic_options[1] in message.data.get("utterance"):
        #         pass
        #     else:
        #         self.speak("Muting volume.")
        #         self.socket_io_emit('volume', '&level=mute', message.data.get('flac_filename'))
        # elif self.server:
        #     if message.data.get("Mic") or self.mic_options[0] in message.data.get("utterance") \
        #             or self.mic_options[1] in message.data.get("utterance"):
        #         self.speak("Microphone muted.")
        #         self.socket_io_emit(event="audio control", kind="microphone", message=False,
        #                             flac_filename=message.data.get("flac_filename"))
        #     else:
        #         self.speak("Audio is going to be muted")
        #         self.socket_io_emit(event="audio control", kind="speech", message=False,
        #                             flac_filename=message.data.get("flac_filename"))
        # else:
        #     if message.data.get("Mic") or self.mic_options[0] in message.data.get("utterance") \
        #             or self.mic_options[1] in message.data.get("utterance"):
        #         self.set_volume(io='input', setting=0)
        #     else:
        #         speak_message = message.data.get('speak_message', True)
        #         if speak_message:
        #             if not self.check_for_signal("use_default_response", -1):
        #                 self.speak_dialog('mute.volume')
        #             else:
        #                 self.speak("Audio is going to be muted")
        #             wait_while_speaking()
        #         self.set_volume(io='output', setting=0)

    # @intent_handler(IntentBuilder("UnmuteVolume").require(
    #    "Volume").require("Unmute"))
    def handle_unmute_volume(self, message):
        if message.data.get("Mic"):
            if request_from_mobile(message):
                self.mobile_skill_intent("microphone", {"state": "unmute"}, message)
                # self.socket_io_emit('microphone', '&state=unmute', message.context["flac_filename"])
            elif self.server:
                self.socket_emit_to_server("audio control",
                                           ["microphone", True, message.context["klat_data"]["request_id"]])
                # self.socket_io_emit(event="audio control", kind="microphone", message=True,
                #                     flac_filename=message.context["flac_filename"])
                self.speak("Microphone listening.", private=True)
            else:
                self.set_volume(io='input', setting=-1)
        else:
            if request_from_mobile(message):
                self.speak("Unmuting volume.", private=True)
                self.mobile_skill_intent("volume", {"level": "unmute"}, message)
                # self.socket_io_emit('volume', '&level=unmute', message.context["flac_filename"])
            elif self.server:
                self.speak("Audio restored.", private=True)
                self.socket_emit_to_server("audio control",
                                           ["speech", True, message.context["klat_data"]["request_id"]])
                # self.socket_io_emit(event="audio control", kind="speech", message=True,
                #                     flac_filename=message.context["flac_filename"])
            else:
                self.set_volume(io='output', setting=-1)

        # if message.data.get("mobile"):
        #     # self.speak("MOBILE-INTENT VOLUME&level=unmute")
        #     self.speak("Unmuting volume.")
        #     self.socket_io_emit('volume', '&level=unmute', message.data.get('flac_filename'))
        # elif self.server:
        #     if message.data.get("Mic") or self.mic_options[0] in message.data.get("utterance") \
        #             or self.mic_options[1] in message.data.get("utterance"):
        #         self.speak("Microphone listening.")
        #         self.socket_io_emit(event="audio control", kind="microphone", message=True,
        #                             flac_filename=message.data.get("flac_filename"))
        #     else:
        #         self.speak("Audio restored.")
        #         self.socket_io_emit(event="audio control", kind="speech", message=True,
        #                             flac_filename=message.data.get("flac_filename"))
        # else:
        #     if message.data.get("Mic") or self.mic_options[0] in message.data.get("utterance") \
        #             or self.mic_options[1] in message.data.get("utterance"):
        #         self.set_volume(io='input', setting=-1)
        #         # LOG.info("in mic")
        #     else:
        #         self.set_volume(io='output', setting=-1)
        #         # speak_message = message.data.get('speak_message', True)
        #         # if speak_message:
        #         #     if not self.check_for_signal("use_default_response", -1):
        #         #         self.speak_dialog('reset.volume',
        #         #                           data={'volume': self.default_level})
        #         #     else:
        #         #         self.speak("Volume restored to {}".format(self.default_level))

    # def volume_to_level(self, volume):
    #     """
    #     Convert a 'volume' to a 'level'
    #
    #     Args:
    #         volume (int): min_volume..max_volume
    #     Returns:
    #         int: the equivalent level
    #     """
    #     range_volume = self.MAX_LEVEL - self.MIN_LEVEL
    #     prop = float(volume - self.min_volume) / self.max_volume
    #     level = int(round(self.MIN_LEVEL + range_volume * prop))
    #     if level > self.MAX_LEVEL:
    #         level = self.MAX_LEVEL
    #     elif level < self.MIN_LEVEL:
    #         level = self.MIN_LEVEL
    #     return level

    # def __level_to_volume(self, level):
    #     """
    #     Convert a 'level' to a 'volume'
    #
    #     Args:
    #         level (int): 0..MAX_LEVEL
    #     Returns:
    #         int: the equivalent volume
    #     """
    #     range = self.max_volume - self.min_volume
    #     prop = float(level) / self.MAX_LEVEL
    #     volume = int(round(self.min_volume + int(range) * prop))

        # return volume

    @staticmethod
    def bound_level(level):
        if level > VolumeSkill.MAX_LEVEL:
            level = VolumeSkill.MAX_LEVEL
        elif level < VolumeSkill.MIN_LEVEL:
            level = VolumeSkill.MIN_LEVEL
        return level

    def update_volume(self, change=0):
        self._get_volume()
        old_level = self.vol_level
        new_level = self.bound_level(old_level + change)
        # self.enclosure.eyes_volume(new_level)
        self.set_volume(io='output', setting=new_level)
        return new_level, new_level != old_level

    def update_mic_volume(self, change=0):
        self._get_volume()
        old_level = self.mic_level
        new_level = self.bound_level(old_level + change)
        # self.enclosure.eyes_volume(new_level)
        self.set_volume(io='input', setting=new_level)
        return new_level, new_level != old_level

    def extract_spoken_volume_level(self, message, default=None):
        level_str = message.data.get('Level', default)
        level = self.default_level
        try:
            level = self.VOLUME_WORDS[level_str]
        except KeyError:
            try:
                level = int(level_str)
                if level <= 10 and "percent" not in message.data.get("utterance"):
                    # Translate 1-10 to 10-100 percent if level is numeric only
                    level = level*10
            except ValueError:
                pass
        level = self.bound_level(level)
        return level


def create_skill():
    return VolumeSkill()
