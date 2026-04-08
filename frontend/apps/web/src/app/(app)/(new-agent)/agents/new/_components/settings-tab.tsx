'use client';

import { useState } from 'react';

import { TabsContent } from '@workspace/ui/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@workspace/ui/components/ui/select';
import { Slider } from '@workspace/ui/components/ui/slider';

import { PROVIDERS, DEFAULT_MODELS, temperatureLabel } from '@/app/(app)/(new-agent)/agents/new/_constants/agent';

export function SettingsTab() {
  const [provider, setProvider] = useState('OpenAI');
  const [model, setModel] = useState('gpt-4.1');
  const [temperature, setTemperature] = useState(0.7);

  const currentProvider = PROVIDERS.find((p) => p.group === provider);

  const handleProviderChange = (val: string) => {
    setProvider(val);
    setModel(DEFAULT_MODELS[val] ?? '');
  };

  return (
    <TabsContent value="settings" className="flex-1 mt-0 overflow-auto">
      <div className="px-6 pt-6 pb-2 max-w-xl">
        <p className="text-xs text-muted-foreground uppercase tracking-wider pb-3 border-b border-border">
          Model
        </p>
      </div>
      <div className="px-6 pb-6 max-w-xl space-y-8">
        <div className="space-y-2">
          <label className="text-sm text-foreground">Provider</label>
          <Select value={provider} onValueChange={handleProviderChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {PROVIDERS.map((p) => (
                <SelectItem key={p.group} value={p.group}>
                  {p.group}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm text-foreground">Model</label>
          <Select value={model} onValueChange={setModel}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>{provider}</SelectLabel>
                {currentProvider?.models.map((m) => (
                  <SelectItem key={m} value={m}>
                    {m}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm text-foreground">Temperature</label>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">
                {temperatureLabel(temperature)}
              </span>
              <span className="text-sm font-mono text-foreground tabular-nums w-8 text-right">
                {temperature.toFixed(1)}
              </span>
            </div>
          </div>
          <Slider
            min={0}
            max={2}
            step={0.1}
            value={[temperature]}
            onValueChange={(value) => setTemperature(value[0] ?? 0.7)}
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0.0</span>
            <span>1.0</span>
            <span>2.0</span>
          </div>
        </div>
      </div>
    </TabsContent>
  );
}
