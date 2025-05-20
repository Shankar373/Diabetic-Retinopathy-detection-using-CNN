import { useEffect, useState } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose: () => void;
}

export function Toast({ message, type, duration = 3000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-green-500" />,
    error: <XCircle className="w-5 h-5 text-red-500" />,
    warning: <AlertTriangle className="w-5 h-5 text-yellow-500" />,
    info: <Info className="w-5 h-5 text-blue-500" />
  };

  return (
    <div className={`
      fixed bottom-4 right-4 flex items-center gap-2 
      px-4 py-3 rounded-lg shadow-lg
      bg-white dark:bg-gray-800
      transform transition-all duration-300
      ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}
    `}>
      {icons[type]}
      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
        {message}
      </p>
    </div>
  );
}
