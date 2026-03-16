import React from 'react';
import { IconType } from 'react-icons';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: IconType;
  bgColor: string;
  textColor: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  bgColor,
  textColor,
}) => {
  return (
    <div className={`${bgColor} rounded-lg shadow-md p-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`${textColor} text-sm font-medium opacity-80`}>{title}</p>
          <p className={`${textColor} text-3xl font-bold mt-2`}>{value}</p>
          {subtitle && (
            <p className={`${textColor} text-xs mt-1 opacity-70 whitespace-pre-line`}>{subtitle}</p>
          )}
        </div>
        <Icon className={`${textColor} opacity-20`} size={48} />
      </div>
    </div>
  );
};

export default StatCard;




