package com.xun.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Skill {

    private Long id;
    /** 标识名，如 "code-review"、"split-java-monolith"，小写字母+数字+连字符 */
    private String name;
    /** 用于前端展示的友好名称 */
    private String displayName;
    /** 描述：做什么 + 什么时候触发 */
    private String description;
    /** Skill 指令主体（Markdown 格式） */
    private String content;
    /** 作者 */
    private String author;
    /** 分类，如 code-review / document-processing / deployment */
    private String category;
    private String createdAt;
    private String updatedAt;
}
