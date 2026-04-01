package com.xun.controller;

import com.xun.common.Result;
import com.xun.model.Skill;
import com.xun.service.SkillService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/skills")
public class SkillController {

    private final SkillService skillService;

    public SkillController(SkillService skillService) {
        this.skillService = skillService;
    }

    @GetMapping
    public Result<List<Skill>> findAll() {
        log.info("查询全部 Skill");
        try {
            List<Skill> skills = skillService.findAll();
            log.info("查询全部 Skill 成功, 共 {} 条", skills.size());
            return Result.success(skills);
        } catch (Exception e) {
            log.error("查询全部 Skill 异常", e);
            return Result.error(500, "查询失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id}")
    public Result<Skill> findById(@PathVariable Long id) {
        log.info("查询 Skill, id={}", id);
        try {
            Skill skill = skillService.findById(id);
            if (skill == null) {
                log.info("Skill 不存在, id={}", id);
                return Result.error(404, "Skill not found");
            }
            log.info("查询 Skill 成功, id={}, name={}", id, skill.getName());
            return Result.success(skill);
        } catch (Exception e) {
            log.error("查询 Skill 异常, id={}", id, e);
            return Result.error(500, "查询失败: " + e.getMessage());
        }
    }

    @PostMapping
    public Result<Skill> create(@RequestBody Skill skill) {
        log.info("新增 Skill, name={}, displayName={}", skill.getName(), skill.getDisplayName());
        try {
            Skill created = skillService.create(skill);
            log.info("新增 Skill 成功, id={}, name={}", created.getId(), created.getName());
            return Result.success(created);
        } catch (Exception e) {
            log.error("新增 Skill 异常, name={}", skill.getName(), e);
            return Result.error(500, "新增失败: " + e.getMessage());
        }
    }

    @PutMapping("/{id}")
    public Result<Skill> update(@PathVariable Long id, @RequestBody Skill skill) {
        log.info("更新 Skill, id={}, name={}", id, skill.getName());
        try {
            Skill updated = skillService.update(id, skill);
            if (updated == null) {
                log.info("更新失败, Skill 不存在, id={}", id);
                return Result.error(404, "Skill not found");
            }
            log.info("更新 Skill 成功, id={}, name={}", id, updated.getName());
            return Result.success(updated);
        } catch (Exception e) {
            log.error("更新 Skill 异常, id={}", id, e);
            return Result.error(500, "更新失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        log.info("删除 Skill, id={}", id);
        try {
            boolean deleted = skillService.delete(id);
            if (!deleted) {
                log.info("删除失败, Skill 不存在, id={}", id);
                return Result.error(404, "Skill not found");
            }
            log.info("删除 Skill 成功, id={}", id);
            return Result.success();
        } catch (Exception e) {
            log.error("删除 Skill 异常, id={}", id, e);
            return Result.error(500, "删除失败: " + e.getMessage());
        }
    }
}
