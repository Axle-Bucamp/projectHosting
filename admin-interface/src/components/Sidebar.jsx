import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FolderOpen,
  Store,
  MessageSquare,
  FileText,
  Settings,
  Shield
} from 'lucide-react';

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projets', href: '/projects', icon: FolderOpen },
  { name: 'Store', href: '/store', icon: Store },
  { name: 'Contacts', href: '/contacts', icon: MessageSquare },
  { name: 'Contenu', href: '/content', icon: FileText },
  { name: 'Système', href: '/system', icon: Settings },
];

const Sidebar = ({ isOpen }) => {
  return (
    <div className={cn(
      "fixed inset-y-0 left-0 z-50 bg-gray-900 transition-all duration-300",
      isOpen ? "w-64" : "w-16"
    )}>
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-center border-b border-gray-800">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            {isOpen && (
              <span className="ml-3 text-white font-semibold">Admin</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "group flex items-center rounded-md px-2 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white"
                )
              }
            >
              <item.icon
                className={cn(
                  "flex-shrink-0 h-5 w-5",
                  isOpen ? "mr-3" : "mx-auto"
                )}
              />
              {isOpen && item.name}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            {isOpen && (
              <span className="ml-2 text-xs text-gray-400">
                Tailscale connecté
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

