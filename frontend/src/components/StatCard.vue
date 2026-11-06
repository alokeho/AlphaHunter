<script setup>
/**
 * 指标卡片。
 *
 * Props:
 * - label: 指标名称
 * - value: 主数值
 * - unit: 单位
 * - hint: 辅助说明
 * - accent: 视觉主题（blue / mint / violet / amber）
 */
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  hint: { type: String, default: '' },
  accent: { type: String, default: 'blue' },
})
</script>

<template>
  <article class="stat-card" :class="`accent-${accent}`">
    <div class="stat-card__top">
      <span class="stat-card__label">{{ label }}</span>
      <span class="stat-card__icon">
        <slot name="icon" />
      </span>
    </div>

    <div class="stat-card__value mono">
      {{ value }}
      <small v-if="unit">{{ unit }}</small>
    </div>

    <div class="stat-card__hint">
      <slot name="hint">{{ hint }}</slot>
    </div>

    <div class="stat-card__wash" aria-hidden="true" />
  </article>
</template>

<style scoped>
.stat-card {
  position: relative;
  min-height: 126px;
  padding: 17px 18px 16px;
  overflow: hidden;
  border: 1px solid var(--ah-border);
  border-radius: var(--ah-radius-lg);
  background: var(--ah-surface);
  box-shadow: var(--ah-shadow-sm);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--ah-shadow);
}

.stat-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.stat-card__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ah-text-soft);
}

.stat-card__icon {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 9px;
  background: var(--stat-wash);
  color: var(--stat-color);
  font-size: 16px;
}

.stat-card__value {
  position: relative;
  z-index: 1;
  margin-top: 9px;
  color: var(--ah-text);
  font-size: 27px;
  font-weight: 750;
  letter-spacing: -0.04em;
  line-height: 1.15;
}

.stat-card__value small {
  margin-left: 4px;
  font-family:
    "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0;
  color: var(--ah-text-faint);
}

.stat-card__hint {
  position: relative;
  z-index: 1;
  margin-top: 7px;
  font-size: 10px;
  color: var(--ah-text-faint);
}

.stat-card__wash {
  position: absolute;
  right: -28px;
  bottom: -34px;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  background: var(--stat-wash);
  opacity: 0.7;
}

.accent-blue {
  --stat-color: #2563eb;
  --stat-wash: #eef4ff;
}

.accent-mint {
  --stat-color: #0f9f7a;
  --stat-wash: #e9faf4;
}

.accent-violet {
  --stat-color: #7152d8;
  --stat-wash: #f2efff;
}

.accent-amber {
  --stat-color: #c46a05;
  --stat-wash: #fff6e8;
}
</style>
