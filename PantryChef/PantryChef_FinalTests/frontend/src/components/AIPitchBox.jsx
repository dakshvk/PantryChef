const AIPitchBox = ({ pitch }) => {
  // Handle pitch as string or object with pitch_text
  const pitchText = typeof pitch === 'string' ? pitch : pitch?.pitch_text || ''
  
  if (!pitchText) return null

  return (
    <div className="mx-4 mt-6 p-4 lg:p-6 bg-emerald-600 rounded-[40px] shadow-sm text-white">
      <div className="flex items-start">
        <div className="text-2xl lg:text-3xl mr-3 lg:mr-4 flex-shrink-0">👨‍🍳</div>
        <div className="flex-1">
          <h3 className="text-lg lg:text-xl font-bold mb-1 lg:mb-2 text-emerald-50">Chef's Recommendation</h3>
          <p className="text-base lg:text-lg leading-snug text-white">{pitchText}</p>
        </div>
      </div>
    </div>
  )
}

export default AIPitchBox

