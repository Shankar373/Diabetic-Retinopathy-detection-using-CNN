"use client";
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Home, Settings, FileText } from 'lucide-react';

export function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/results', label: 'Results', icon: FileText },
    { href: '/config', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            {links.map(({ href, label, icon: Icon }) => (
              <Link
                key={label}
                href={href}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium
                  ${pathname === href
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                  }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
