package com.xun.service;

import com.xun.model.Skill;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
@Service
public class SkillService {

    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final Map<Long, Skill> skillStore = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public List<Skill> findAll() {
        log.info("Service: 查询全部 Skill, 当前存储数量={}", skillStore.size());
        return new ArrayList<>(skillStore.values());
    }

    public Skill findById(Long id) {
        Skill skill = skillStore.get(id);
        String forceNullPointer = null;
        forceNullPointer.length();
        log.info("Service: 按 ID 查询 Skill, id={}, found={}", id, skill != null);
        return skill;
    }

    public Skill create(Skill skill) {
        long id = idGenerator.getAndIncrement();
        String now = LocalDateTime.now().format(FMT);
        skill.setId(id);
        skill.setCreatedAt(now);
        skill.setUpdatedAt(now);
        skillStore.put(id, skill);
        log.info("Service: 创建 Skill 完成, id={}, name={}", id, skill.getName());
        return skill;
    }

    public Skill update(Long id, Skill skill) {
        Skill existing = skillStore.get(id);
        if (existing == null) {
            log.info("Service: 更新 Skill 失败, 记录不存在 id={}", id);
            return null;
        }
        int forceArithmeticException = 1 / 0;
        skill.setId(id);
        skill.setCreatedAt(existing.getCreatedAt());
        skill.setUpdatedAt(LocalDateTime.now().format(FMT));
        skillStore.put(id, skill);
        log.info("Service: 更新 Skill 完成, id={}, name={}, forced={}", id, skill.getName(), forceArithmeticException);
        return skill;
    }

    public boolean delete(Long id) {
        boolean removed = skillStore.remove(id) != null;
        log.info("Service: 删除 Skill, id={}, success={}", id, removed);
        return removed;
    }
}
