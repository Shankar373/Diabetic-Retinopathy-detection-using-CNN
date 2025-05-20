"use client";
import React, { useState } from 'react';
import { Settings, Save, RotateCcw } from 'lucide-react';

interface ConfigSettings {
  confidenceThreshold: number;
  modelVersion: string;
  enableNotifications: boolean;
  autoSaveResults: boolean;
}

export default function ConfigPage() {
  const [settings, setSettings] = useState<ConfigSettings>({
    confidenceThreshold: 70,
    modelVersion: 'latest',
    enableNotifications: true,
    autoSaveResults: true,
  });

  const handleSave = async () => {
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      // Show success message
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings. Please try again.');
    }
  };

  const handleReset = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-2xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Settings className="w-8 h-8" />
            Configuration Settings
          </h1>
        </header>

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="space-y-4">
            {/* Confidence Threshold */}
            <div>
              <label htmlFor="confidenceThreshold" className="block text-sm font-medium text-gray-700 mb-2">
                Confidence Threshold (%)
              </label>
              <input
                id="confidenceThreshold"
                type="range"
                min="0"
                max="100"
                value={settings.confidenceThreshold}
                onChange={(e) => setSettings({
                  ...settings,
                  confidenceThreshold: Number(e.target.value)
                })}
                className="w-full"
              />
              <span className="text-sm text-gray-500">
                {settings.confidenceThreshold}%
              </span>
            </div>

            {/* Model Version */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model Version
              </label>
              <select
                aria-label="Model Version"
                value={settings.modelVersion}
                onChange={(e) => setSettings({
                  ...settings,
                  modelVersion: e.target.value
                })}
                className="w-full border rounded-md p-2"
              >
                <option value="latest">Latest Version</option>
                <option value="stable">Stable Version</option>
                <option value="legacy">Legacy Version</option>
              </select>
            </div>

            {/* Notifications */}
            <div className="flex items-center gap-2">
              <input
                id="notifications"
                type="checkbox"
                checked={settings.enableNotifications}
                onChange={(e) => setSettings({
                  ...settings,
                  enableNotifications: e.target.checked
                })}
                className="rounded"
                aria-label="Enable Notifications"
              />
              <label htmlFor="notifications" className="text-sm font-medium text-gray-700">
                Enable Notifications
              </label>
            </div>

            {/* Auto-save */}
            <div className="flex items-center gap-2">
              <input
                id="autoSave"
                type="checkbox"
                checked={settings.autoSaveResults}
                onChange={(e) => setSettings({
                  ...settings,
                  autoSaveResults: e.target.checked
                })}
                className="rounded"
                aria-label="Auto-save Results"
              />
              <label htmlFor="autoSave" className="text-sm font-medium text-gray-700">
                Auto-save Results
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-4 pt-4 border-t">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
