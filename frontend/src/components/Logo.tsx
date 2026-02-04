interface LogoProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function GujRAMLogo({ className = '', size = 'md' }: LogoProps) {
  const sizeClasses = {
    sm: 'h-12 w-12',
    md: 'h-16 w-16',
    lg: 'h-24 w-24'
  }

  return (
    <div className={`flex items-center ${className}`}>
      <div className={`${sizeClasses[size]} flex-shrink-0`}>
        <img 
          src="/judgement.png" 
          alt="GujRAM Logo" 
          className="w-full h-full object-contain"
        />
      </div>
    </div>
  )
}

export function GujaratPoliceLogo({ className = '', size = 'md' }: LogoProps) {
  const sizeClasses = {
    sm: 'h-16 w-12',
    md: 'h-20 w-15',
    lg: 'h-32 w-24'
  }

  return (
    <div className={`flex items-center ${className}`}>
      <div className={`${sizeClasses[size]} flex-shrink-0`}>
        <img 
          src="/police_logo.png" 
          alt="Gujarat Police Logo" 
          className="w-full h-full object-contain"
        />
      </div>
    </div>
  )
}
