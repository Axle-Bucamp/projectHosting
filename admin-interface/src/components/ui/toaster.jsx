import React, { createContext, useContext } from 'react';
import { useToast } from '@/hooks/use-toast';

const ToastContext = createContext();

export function ToasterProvider({ children }) {
  const { toasts } = useToast();

  return (
    <ToastContext.Provider value={{}}>
      {children}
      <div
        aria-live="assertive"
        className="fixed top-5 right-5 flex flex-col space-y-2 z-50"
      >
        {toasts.map(({ id, title, description, open }) =>
          open ? (
            <div key={id} className="bg-blue-600 text-white px-4 py-2 rounded shadow">
              {title}
              {description && <div>{description}</div>}
            </div>
          ) : null
        )}
      </div>
    </ToastContext.Provider>
  );
}

export function Toaster() {
  // Placeholder component if you want to extend or add static markup
  return null;
}
