import React, { useState } from 'react';
import ChatTab from './HermesPage/ChatTab';
import MemoryTab from './HermesPage/MemoryTab';
import SkillsTab from './HermesPage/SkillsTab';
import InspectorTab from './HermesPage/InspectorTab';

export default function HermesPage() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">AI Assistant</h1>
      </div>

      <div className="mb-4">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Chat
            </button>
            <button
              onClick={() => setActiveTab('memory')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'memory'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Memory
            </button>
            <button
              onClick={() => setActiveTab('skills')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'skills'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Skills
            </button>
            <button
              onClick={() => setActiveTab('inspector')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'inspector'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Inspector
            </button>
          </nav>
        </div>
      </div>

      <div className="mt-6">
        {activeTab === 'chat' && <ChatTab />}
        {activeTab === 'memory' && <MemoryTab />}
        {activeTab === 'skills' && <SkillsTab />}
        {activeTab === 'inspector' && <InspectorTab />}
      </div>
    </div>
  );
}