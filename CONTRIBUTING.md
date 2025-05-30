# 开发贡献指南

## 核心原则

### 1. 代码修改原则
- **保持功能完整性**：修改代码时不能影响其他已经实现的功能
- **向后兼容**：新功能的添加不应破坏现有功能的行为
- **测试优先**：所有修改必须经过充分测试后才能合并到主分支

### 2. 发布流程
- **测试验证**：新功能必须经过完整测试并验证无误
- **分步发布**：代码修改后不立即更新安装包，需经过以下步骤：
  1. 完成代码修改
  2. 进行功能测试
  3. 确认功能正常
  4. 获得批准后再更新安装包

### 3. 代码风格
- 使用统一的代码格式化规则
- 保持代码注释的完整性和清晰度
- 遵循 Python PEP 8 编码规范

### 4. 文档维护
- 及时更新相关文档
- 保持文档与代码的一致性
- 记录重要的设计决策和变更原因

### 5. 版本控制
- 使用语义化版本号
- 保持提交信息的清晰和规范
- 重要变更必须记录在更新日志中

## 开发流程

### 1. 功能开发
1. 创建功能分支
2. 编写代码和测试
3. 进行代码审查
4. 合并到主分支

### 2. 测试验证
1. 单元测试
2. 功能测试
3. 集成测试
4. 用户验收测试

### 3. 发布流程
1. 代码审查通过
2. 测试验证完成
3. 文档更新完成
4. 创建发布标签
5. 构建安装包
6. 发布新版本

## 注意事项
- 所有重大变更必须经过讨论和批准
- 保持代码库的整洁和可维护性
- 定期进行代码重构和优化
- 及时响应问题报告和修复缺陷