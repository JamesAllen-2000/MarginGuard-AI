import { FC, ReactNode, CSSProperties } from 'react';

interface GlassPanelProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export const GlassPanel: FC<GlassPanelProps> = ({ children, className = '', style }) => {
  return (
    <div className={`glass-panel ${className}`} style={style}>
      {children}
    </div>
  );
};
