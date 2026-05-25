// L3 only
export default {
  mutate: ['src/**/*.ts', '!src/**/*.d.ts'],
  testRunner: 'vitest',
  reporters: ['clear-text', 'html'],
  thresholds: { high: 80, low: 60, break: 50 },
  vitest: { configFile: 'vitest.config.ts' },
}
