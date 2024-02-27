from gtts import gTTS
import configparser

def create_voice_over(fileName, text, language='en', pitch_factor=2.0, rate_factor=1.1):
    config = configparser.ConfigParser()
    config.read('config.ini')
    voiceoverDir = config["General"]["TemplateDirectory"]
    filePath = f"{voiceoverDir}/{fileName}.mp3"
    
    tts = gTTS(text=text, lang=language)
    tts.save(filePath)

    return filePath