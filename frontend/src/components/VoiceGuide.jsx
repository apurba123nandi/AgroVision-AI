import React from 'react';
import { TextToSpeech } from '@capacitor-community/text-to-speech';
import { Volume2, Play, Pause } from 'lucide-react';

const VoiceGuide = ({ result, t, language }) => {
  const [speaking, setSpeaking] = React.useState(false);

  const getTranslatedText = () => {
    if (!result) return "";
    if (language === 'en') return result.treatment || result.recommendation || "";
    
    // Logic to select correct translation key
    const d = result.disease?.toLowerCase() || "";
    const s = result.severity?.toLowerCase() || "";
    
    if (d.includes('healthy')) return t.recHealthy;
    if (d.includes('powdery')) {
      if (s === 'low') return t.recPowderyLow;
      if (s === 'medium') return t.recPowderyMed;
      return t.recPowderyHigh;
    }
    if (d.includes('rust')) {
      if (s === 'low') return t.recRustLow;
      if (s === 'medium') return t.recRustMed;
      return t.recRustHigh;
    }
    return result.treatment || result.recommendation || "";
  };

  const speak = async () => {
    const textToSpeak = getTranslatedText();
    if (!textToSpeak) return;
    
    try {
      setSpeaking(true);
      await TextToSpeech.speak({
        text: textToSpeak,
        lang: language === 'te' ? 'te-IN' : language === 'hi' ? 'hi-IN' : 'en-US',
        rate: 0.8, // Slow pace for farmers
        pitch: 1.0,
        volume: 1.0,
        category: 'ambient',
      });
    } catch (error) {
      console.error('TTS Error:', error);
    } finally {
      setSpeaking(false);
    }
  };

  const stop = async () => {
    await TextToSpeech.stop();
    setSpeaking(false);
  };

  return (
    <div className="voice-guide-container" style={{ marginTop: '1rem' }}>
      <button 
        onClick={speaking ? stop : speak}
        className={speaking ? "secondary-button" : "primary-button"}
        style={{ width: '100%', gap: '1rem' }}
      >
        {speaking ? <Pause size={24} /> : <Volume2 size={24} />}
        <span>{speaking ? "Stop Voice Guide" : "Listen to Remedy"}</span>
      </button>
    </div>
  );
};

export default VoiceGuide;
