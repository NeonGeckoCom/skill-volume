# <img src='https://0000.us/klatchat/app/files/neon_images/icons/neon_skill.png' card_color="#FF8600" width="50" style="vertical-align:bottom">Volume
  
## Summary  
  
Control microphone and speaker audio levels.
  
## Requirements  
[PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio/) is required and installed by default with most Linux
distributions.
  
## Description  
  
This skill controls the audio level and mute status for the default input and output device. You may increment volume,
set to a specified level, or mute/unmute. You may also query the current volume and microphone level.
    
  
  
## Examples  
  
First, make your request:  
  
Say `“Hey Neon”` if you are in the wake words mode.
  
- "mute speakers"
      
- "unmute speakers"
      
- “set microphone to 70 percent”
      
- “decrease volume”

- "what is the volume"
      
  
Neon will respond with the new audio level.

## Location  
  

     ${skills}/volume.neon

## Files
<details>
<summary>Click to expand.</summary>
<br>

    ${skills}/volume.neon/
    ${skills}/volume.neon/.gitignore
    ${skills}/volume.neon/__pycache__
    ${skills}/volume.neon/__pycache__/__init__.cpython-36.pyc
    ${skills}/volume.neon/vocab
    ${skills}/volume.neon/vocab/en-us
    ${skills}/volume.neon/vocab/en-us/Volume.voc
    ${skills}/volume.neon/vocab/en-us/Increase.voc
    ${skills}/volume.neon/vocab/en-us/Query.voc
    ${skills}/volume.neon/vocab/en-us/Mute.voc
    ${skills}/volume.neon/vocab/en-us/Level.voc
    ${skills}/volume.neon/vocab/en-us/Mic.voc
    ${skills}/volume.neon/vocab/en-us/Percent.voc
    ${skills}/volume.neon/vocab/en-us/Unmute.voc
    ${skills}/volume.neon/vocab/en-us/Decrease.voc
    ${skills}/volume.neon/vocab/de-de
    ${skills}/volume.neon/vocab/de-de/Volume.voc
    ${skills}/volume.neon/vocab/de-de/Increase.voc
    ${skills}/volume.neon/vocab/de-de/Mute.voc
    ${skills}/volume.neon/vocab/de-de/Level.voc
    ${skills}/volume.neon/vocab/de-de/Unmute.voc
    ${skills}/volume.neon/vocab/de-de/Decrease.voc
    ${skills}/volume.neon/vocab/es-es
    ${skills}/volume.neon/vocab/es-es/Volume.voc
    ${skills}/volume.neon/vocab/es-es/Increase.voc
    ${skills}/volume.neon/vocab/es-es/Mute.voc
    ${skills}/volume.neon/vocab/es-es/Level.voc
    ${skills}/volume.neon/vocab/es-es/Unmute.voc
    ${skills}/volume.neon/vocab/es-es/Decrease.voc
    ${skills}/volume.neon/vocab/it-it
    ${skills}/volume.neon/vocab/it-it/Volume.voc
    ${skills}/volume.neon/vocab/it-it/Increase.voc
    ${skills}/volume.neon/vocab/it-it/Mute.voc
    ${skills}/volume.neon/vocab/it-it/Level.voc
    ${skills}/volume.neon/vocab/it-it/Unmute.voc
    ${skills}/volume.neon/vocab/it-it/Decrease.voc
    ${skills}/volume.neon/README.md
    ${skills}/volume.neon/regex
    ${skills}/volume.neon/regex/en-us
    ${skills}/volume.neon/regex/en-us/volume.amount.rx
    ${skills}/volume.neon/regex/de-de
    ${skills}/volume.neon/regex/de-de/volume.amount.rx
    ${skills}/volume.neon/regex/es-es
    ${skills}/volume.neon/regex/es-es/volume.amount.rx
    ${skills}/volume.neon/regex/it-it
    ${skills}/volume.neon/regex/it-it/volume.amount.rx
    ${skills}/volume.neon/blop-mark-diangelo.wav
    ${skills}/volume.neon/README.old
    ${skills}/volume.neon/__init__.py
    ${skills}/volume.neon/test
    ${skills}/volume.neon/test/intent
    ${skills}/volume.neon/test/intent/sample7.intent.json
    ${skills}/volume.neon/test/intent/sample6.intent.json
    ${skills}/volume.neon/test/intent/sample3.intent.json
    ${skills}/volume.neon/test/intent/sample2.intent.json
    ${skills}/volume.neon/test/intent/sample1.intent.json
    ${skills}/volume.neon/test/intent/sample4.intent.json
    ${skills}/volume.neon/test/intent/sample8.intent.json
    ${skills}/volume.neon/test/intent/sample10.intent.json
    ${skills}/volume.neon/test/intent/sample9.intent.json
    ${skills}/volume.neon/test/intent/sample5.intent.json
    ${skills}/volume.neon/dialog
    ${skills}/volume.neon/dialog/en-us
    ${skills}/volume.neon/dialog/en-us/mute.volume.dialog
    ${skills}/volume.neon/dialog/en-us/increase.volume.dialog
    ${skills}/volume.neon/dialog/en-us/set.volume.dialog
    ${skills}/volume.neon/dialog/en-us/decrease.volume.dialog
    ${skills}/volume.neon/dialog/en-us/volume.is.dialog
    ${skills}/volume.neon/dialog/en-us/already.max.volume.dialog
    ${skills}/volume.neon/dialog/en-us/reset.volume.dialog
    ${skills}/volume.neon/dialog/de-de
    ${skills}/volume.neon/dialog/de-de/mute.volume.dialog
    ${skills}/volume.neon/dialog/de-de/increase.volume.dialog
    ${skills}/volume.neon/dialog/de-de/set.volume.dialog
    ${skills}/volume.neon/dialog/de-de/decrease.volume.dialog
    ${skills}/volume.neon/dialog/de-de/volume.is.dialog
    ${skills}/volume.neon/dialog/de-de/already.max.volume.dialog
    ${skills}/volume.neon/dialog/de-de/reset.volume.dialog
    ${skills}/volume.neon/dialog/es-es
    ${skills}/volume.neon/dialog/es-es/mute.volume.dialog
    ${skills}/volume.neon/dialog/es-es/increase.volume.dialog
    ${skills}/volume.neon/dialog/es-es/set.volume.dialog
    ${skills}/volume.neon/dialog/es-es/decrease.volume.dialog
    ${skills}/volume.neon/dialog/es-es/volume.is.dialog
    ${skills}/volume.neon/dialog/es-es/already.max.volume.dialog
    ${skills}/volume.neon/dialog/es-es/reset.volume.dialog
    ${skills}/volume.neon/dialog/it-it
    ${skills}/volume.neon/dialog/it-it/mute.volume.dialog
    ${skills}/volume.neon/dialog/it-it/increase.volume.dialog
    ${skills}/volume.neon/dialog/it-it/set.volume.dialog
    ${skills}/volume.neon/dialog/it-it/decrease.volume.dialog
    ${skills}/volume.neon/dialog/it-it/volume.is.dialog
    ${skills}/volume.neon/dialog/it-it/already.max.volume.dialog
    ${skills}/volume.neon/dialog/it-it/reset.volume.dialog
    ${skills}/volume.neon/settings.json
    ${skills}/volume.neon/LICENSE


</details>
  

## Class Diagram
[Click Here](https://0000.us/klatchat/app/files/neon_images/class_diagrams/volume.png)
  

## Available Intents
<details>
<summary>Show list</summary>
<br>


### Decrease.voc

    lower
    reduce
    decrease
    turn down
    quieter
    less loud


### Increase.voc

    rise
    raise
    boost
    increase
    turn up
    louder


### Level.voc

    #
    ##
    quiet
    normal
    loud

### Mic.voc

    mic
    microphone

### Mute.voc

    mute
    silence

### Percent.voc

    percent

### Query.voc

    what
    tell me
    get
    say
    speak
    
### Unmute.voc

    reset
    unmute
    restore
    
### Volume.voc

    volume
    speaker
    sound
    mic
    microphone
    input
    level
    talk

</details>


## Details

### Text

	    Unmute volume
	    >> Volume restored to 90.
	    
	    Decrease volume
	    >> Volume set to 80 percent.
	    
	    What is the microphone level?
	    >> The microphone level is at 70 percent.
	    

### Picture

### Video

## Troubleshooting
Make sure the correct default audio devices are selected (see `3. Setting Up Hardware` in the instructions).

## Contact Support
Use the [link](https://neongecko.com/ContactUs) or [submit an issue on GitHub](https://help.github.com/en/articles/creating-an-issue)

## Credits
reginaneon [neongeckocom](https://neongecko.com/) djmcknight358 Mycroft AI
