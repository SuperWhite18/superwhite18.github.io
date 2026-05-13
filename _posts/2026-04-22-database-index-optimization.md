---
layout: post
title: "数据库索引优化实战：从慢查询到毫秒级响应的调优之旅"
date: 2026-04-22
tags: [Database, Performance, PostgreSQL]
read_time: "4 分钟"
---

一个真实的生产环境慢查询优化案例。从 EXPLAIN 分析到复合索引设计，再到覆盖索引与索引条件下推的巧妙运用。

## 问题发现

监控告警：某查询 P99 延迟飙升至 3.2 秒。查询本身并不复杂：

```sql
SELECT * FROM orders
WHERE user_id = $1 AND status = $2
ORDER BY created_at DESC
LIMIT 20;
```

## 分析过程

`EXPLAIN ANALYZE` 显示使用了 `user_id` 上的单列索引，但需要回表过滤 `status` 和排序 `created_at`。

## 优化方案

创建复合索引：

```sql
CREATE INDEX idx_orders_user_status_created
ON orders (user_id, status, created_at DESC);
```

优化后 P99 降至 8ms。关键点：

1. 索引列顺序：等值条件在前，范围/排序在后
2. 覆盖索引避免回表
3. `DESC` 在索引中支持反向排序
