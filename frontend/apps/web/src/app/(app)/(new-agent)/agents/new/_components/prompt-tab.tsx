'use client';

import { useState } from 'react';

import { TabsContent } from '@workspace/ui/components/ui/tabs';
import { Textarea } from '@workspace/ui/components/ui/textarea';

export function PromptTab() {
  const [prompt, setPrompt] = useState('');

  return (
    <TabsContent value="prompt" className="flex-1 mt-0 p-6 flex flex-col min-h-0">
      <Textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt here..."
        className="w-full flex-1 resize-none min-h-0"
      />
    </TabsContent>
  );
}
