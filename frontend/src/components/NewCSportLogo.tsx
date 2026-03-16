import React from 'react';

interface NewCSportLogoProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'default' | 'white';
}

const NewCSportLogo: React.FC<NewCSportLogoProps> = ({ 
  size = 'medium', 
  color = 'default' 
}) => {
  const sizeClasses = {
    small: 'text-2xl',
    medium: 'text-5xl',
    large: 'text-6xl'
  };

  const sportSizeClasses = {
    small: 'text-xs',
    medium: 'text-xl',
    large: 'text-2xl'
  };

  const colorClasses = {
    default: {
      new: 'text-blue-600',
      c: 'text-orange-500',
      sport: 'text-gray-700'
    },
    white: {
      new: 'text-white',
      c: 'text-orange-400',
      sport: 'text-white'
    }
  };

  const colors = colorClasses[color];

  return (
    <div className="flex items-center justify-center">
      <div className="text-center">
        <div className={`${sizeClasses[size]} font-bold leading-none`}>
          <span className={colors.new}>New</span>
          <span className={colors.c}>C</span>
        </div>
        <div className={`${sportSizeClasses[size]} font-semibold ${colors.sport} -mt-1`}>
          SPORT
        </div>
      </div>
    </div>
  );
};

export default NewCSportLogo;



