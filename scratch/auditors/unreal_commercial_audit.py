#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   💼 Unreal Engine Commercial & Publisher Enterprise Auditor 3.0           ║
║   60+ Non-Technical Commercial Readiness, Market Fit & Publisher Scanner  ║
║                                                                           ║
║   PURPOSE: Comprehensive 60-Question Commercial Audit covering 10 domains:║
║   - Target Market & Studio Segmentation (AAA, VR, Simulators)            ║
║   - Commercial Pricing Power & ROI Justification ($99-$499/yr)            ║
║   - Open-Core vs Paid Pro Upgrade Triggers                                ║
║   - No-Code Blueprint UX Ergonomics for Game Designers                    ║
║   - Editor Utility Widgets (EUW) & In-Editor Workflows                    ║
║   - Onboarding Friction & Plug-and-Play Demo Maps (/Content/Maps/)        ║
║   - Technical Artist Presets & Material Systems                           ║
║   - Support Burden & UE Version Migration Overhead                        ║
║   - Epic Fab Marketplace EULA & Legal Safety                              ║
║   - Community Social Proof & B2B Enterprise Custom Support                ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/unreal_commercial_audit.py /path/to/ue_plugin [PluginName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class CommercialQuestion:
    """Documentation for CommercialQuestion."""
    domain: str             # TARGET_MARKET / PRICING / FREEMIUM / NOCODE_UX / EDITOR_EUW / ONBOARDING / ARTIST_PRESETS / SUPPORT / LEGAL / COMMUNITY
    question_id: str        # COM-001..COM-060
    question: str
    tokens: list[str]
    weight: int             # 1-5
    impact: str             # HIGH_VALUE / MEDIUM_VALUE / RISK
    evidence: list[str] = field(default_factory=list)
    actionable_insight: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 60 Commercial & Publisher Questions Registry
# ─────────────────────────────────────────────────────────────────────────────
COMMERCIAL_QUESTIONS: list[CommercialQuestion] = [

    # ── 1. TARGET MARKET & STUDIO SEGMENTATION (6 Questions) ─────────────────
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-001", weight=5, impact="HIGH_VALUE",
        question="Ориентирован ли плагин на высокобюджетные B2B секторы (AAA, Virtual Production, VR, Симуляторы)?",
        tokens=["Enterprise", "VirtualProduction", "VR", "Simulator", "Multiplayer", "AAA"],
        actionable_insight="Предложите Enterprise Custom License Tier ($499–$1,999/год) вместе с Fab Marketplace retail ($49–$99).",
    ),
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-002", weight=4, impact="HIGH_VALUE",
        question="Поддерживаются ли мультиплеерные dedicated сервера для сетевых онлайн-игр?",
        tokens=["DedicatedServer", "Multiplayer", "Server", "Replication", "Network"],
        actionable_insight="Сетевые студии платят в 3x больше за плагины с готовой поддержкой Dedicated Server.",
    ),
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-003", weight=4, impact="HIGH_VALUE",
        question="Есть ли поддержка мобильных платформ (iOS / Android)?",
        tokens=["iOS", "Android", "Mobile", "Touch"],
        actionable_insight="Опубликуйте плашку 'Mobile Ready' для увеличения объема продаж мобильным разработчикам.",
    ),
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-004", weight=4, impact="HIGH_VALUE",
        question="Есть ли поддержка консольных платформ (PS5 / Xbox Series / Nintendo Switch)?",
        tokens=["PS5", "Xbox", "Switch", "Console"],
        actionable_insight="Продавайте коммерческие лицензии консольным разработчикам по завышенному тарифу.",
    ),
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-005", weight=4, impact="HIGH_VALUE",
        question="Ориентирован ли плагин на архитектурную визуализацию и метавселенные (ArchViz / Automotive)?",
        tokens=["ArchViz", "Automotive", "Datasmith", "Visualization", "RealEstate"],
        actionable_insight="Студии архитектуры готов платить от $299 за плагин, экономящий время визуализации.",
    ),
    CommercialQuestion(
        domain="TARGET_MARKET", question_id="COM-006", weight=4, impact="HIGH_VALUE",
        question="Поддерживает ли плагин шлемы виртуальной и дополненной реальности (OpenXR / VisionOS)?",
        tokens=["OpenXR", "VR", "AR", "Headset", "MotionController"],
        actionable_insight="Выделите тег 'XR Ready' для привлечения покупателей из корпоративного VR-обучения.",
    ),

    # ── 2. COMMERCIAL PRICING POWER & ROI JUSTIFICATION (6 Questions) ───────
    CommercialQuestion(
        domain="PRICING", question_id="COM-007", weight=5, impact="HIGH_VALUE",
        question="Экономит ли плагин покупателю 80+ часов C++ разработки, оправдывая ценник $99–$249?",
        tokens=["Hours", "Save", "Performance", "Optimization", "Speedup"],
        actionable_insight="Укажите 'Экономит 80+ часов разработки C++' в заглавии листинга на Fab Marketplace.",
    ),
    CommercialQuestion(
        domain="PRICING", question_id="COM-008", weight=4, impact="HIGH_VALUE",
        question="Заменяет ли плагин собой подписку на дорогостоящие внешние SaaS сервисы?",
        tokens=["SaaS", "Subscription", "Cloud", "Service", "Cost"],
        actionable_insight="Позиционируйте плагин как разовую покупку без ежемесячных платежей.",
    ),
    CommercialQuestion(
        domain="PRICING", question_id="COM-009", weight=4, impact="HIGH_VALUE",
        question="Содержит ли плагин готовые пресеты, позволяющие запустить фичу за 5 минут?",
        tokens=["Preset", "QuickStart", "Template", "5min"],
        actionable_insight="Маркетинговый акцент на мгновенный запуск поднимает конверсию листинга в 2 раза.",
    ),
    CommercialQuestion(
        domain="PRICING", question_id="COM-010", weight=4, impact="HIGH_VALUE",
        question="Есть ли возможность продавать дополнительные контент-паки (Add-ons / Content Packs)?",
        tokens=["Addon", "ExtensionPack", "ContentPack", "Extra"],
        actionable_insight="Создайте экосистему платных аддонов по $19-$29 для повторных продаж существующим покупателям.",
    ),
    CommercialQuestion(
        domain="PRICING", question_id="COM-011", weight=4, impact="HIGH_VALUE",
        question="Оправдана ли продажа плагина по модели безлимитных исходников (Full C++ Source Code)?",
        tokens=["SourceCode", "FullSource", "C++", "SourceIncluded"],
        actionable_insight="Студии покупают исходники по тарифу $199+, открывая доступ к кастомизации под свои нужды.",
    ),
    CommercialQuestion(
        domain="PRICING", question_id="COM-012", weight=4, impact="HIGH_VALUE",
        question="Есть ли встроенный механизм лимитирования бесплатной версии (Watermark / Trial Limit)?",
        tokens=["Trial", "Watermark", "Limit", "FreeVersion"],
        actionable_insight="Используйте водяной знак в бесплатной версии на GitHub для драйва продаж платной версии.",
    ),

    # ── 3. OPEN-CORE VS PAID PRO UPGRADE TRIGGERS (6 Questions) ──────────────
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-013", weight=5, impact="HIGH_VALUE",
        question="Четко ли разделен код на бесплатный Open-Core и платные Pro модули?",
        tokens=["Pro", "Free", "Commercial", "License", "Paid", "Premium"],
        actionable_insight="Бесплатное ядро привлекает сообщество, а Pro-модули генерируют основной поток выручки.",
    ),
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-014", weight=4, impact="HIGH_VALUE",
        question="Вынесены ли коммерческие фичи в закрытые динамические библиотеки (.dll / .so / .dylib)?",
        tokens=["DLL", "PluginBinary", "Compiled", "BinaryOnly"],
        actionable_insight="Позволяет поставлять Pro-версию без раскрытия компрометирующих бизнес-алгоритмов.",
    ),
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-015", weight=4, impact="HIGH_VALUE",
        question="Есть ли встроенная проверка коммерческой лицензии или подписи плагина?",
        tokens=["LicenseKey", "Validation", "Signature", "VerifyLicense"],
        actionable_insight="Защищает плагин от нелицензионного использования в коммерческих игровых проектах.",
    ),
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-016", weight=4, impact="HIGH_VALUE",
        question="Доступны ли расширенные инструменты аналитики производительности только в Pro версии?",
        tokens=["Profiler", "Analytics", "Metrics", "ProTools"],
        actionable_insight="Отличный триггер для апгрейда коммерческими студиями на этапе оптимизации перед релизом.",
    ),
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-017", weight=4, impact="HIGH_VALUE",
        question="Предлагается ли платный модуль интеграции с облачными серверами (AWS / Firebase / PlayFab)?",
        tokens=["PlayFab", "AWS", "Firebase", "BackendIntegration"],
        actionable_insight="Продавайте облачные интеграции отдельным коммерческим плагином.",
    ),
    CommercialQuestion(
        domain="FREEMIUM", question_id="COM-018", weight=4, impact="HIGH_VALUE",
        question="Есть ли опция покупки подписки на приоритетные обновления и ранний доступ к бэтам?",
        tokens=["Beta", "EarlyAccess", "PriorityUpdates", "VIP"],
        actionable_insight="Обеспечивает прогнозируемый рекуррентный доход через Boosty / Patreon.",
    ),

    # ── 4. NO-CODE BLUEPRINT UX FOR GAME DESIGNERS (6 Questions) ─────────────
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-019", weight=5, impact="HIGH_VALUE",
        question="Доступно ли 100% функционала геймдизайнерам без написания кода C++ (BlueprintCallable)?",
        tokens=["BlueprintCallable", "BlueprintPure", "BlueprintType", "BlueprintAssignable"],
        actionable_insight="Увеличивает целевую аудиторию покупателей в 5 раз (дизайнеров больше, чем C++ программистов).",
    ),
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-020", weight=4, impact="HIGH_VALUE",
        question="Понятно ли структурированы категории Blueprint нод (`Category = 'MyPlugin|Core'`)?",
        tokens=["Category", "DisplayName", "Keywords", "ToolTip"],
        actionable_insight="Удобная категория нод в меню Blueprint сокращает время поиска нужной функции до 2 секунд.",
    ),
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-021", weight=4, impact="HIGH_VALUE",
        question="Есть ли информативные подсказки (ToolTips) у всех параметров нод в редакторе?",
        tokens=["ToolTip", "DocString", "HelpText", "Description"],
        actionable_insight="Всплывающие подсказки избавляют покупателя от необходимости постоянно читать документацию.",
    ),
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-022", weight=4, impact="HIGH_VALUE",
        question="Используются ли удобные Blueprint Enum выборы вместо невнятных чисел или строк?",
        tokens=["UENUM", "Enum", "BlueprintType", "DisplayNames"],
        actionable_insight="Предотвращает ошибки дизайнеров при выборе режимов работы плагина.",
    ),
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-023", weight=4, impact="HIGH_VALUE",
        question="Есть ли понятные Blueprint события (Event Delegates) для отслеживания результатов?",
        tokens=["DECLARE_DYNAMIC_MULTICAST_DELEGATE", "Event", "OnSuccess", "OnFailure"],
        actionable_insight="Позволяет легко навешивать логику на события без написания опросов (polling).",
    ),
    CommercialQuestion(
        domain="NOCODE_UX", question_id="COM-024", weight=4, impact="HIGH_VALUE",
        question="Безопасны ли Blueprint ноды от вызовов с нулевыми указателями (`NULL` Checks)?",
        tokens=["IsValid", "NullCheck", "Ensure", "Check"],
        actionable_insight="Предотвращает падения редактора (Editor Crash) при неверных действиях дизайнера.",
    ),

    # ── 5. EDITOR EXTENSIONS & UTILITY WIDGETS (EUW) (6 Questions) ────────────
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-025", weight=5, impact="HIGH_VALUE",
        question="Включены ли в плагин пользовательские утилиты редактора (Editor Utility Widgets / EUW)?",
        tokens=["EditorUtilityWidget", "EUW", "EditorSubsystem", "Blutility"],
        actionable_insight="Позиционируйте плагин как инструментарий для автоматизации рутины внутри UE Editor.",
    ),
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-026", weight=4, impact="HIGH_VALUE",
        question="Есть ли визуальное окно настроек плагина в Project Settings (`ISettingsModule`)?",
        tokens=["ISettingsModule", "ProjectSettings", "DeveloperSettings"],
        actionable_insight="Глобальные настройки проекта в одном окне повышают профессиональный вид плагина.",
    ),
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-027", weight=4, impact="HIGH_VALUE",
        question="Добавляет ли плагин удобные кнопки во встроенную панель редактора (Toolbar Buttons)?",
        tokens=["FUICommandInfo", "FExtender", "Toolbar", "MenuBuilder"],
        actionable_insight="Доступ к основным функциям в 1 клик прямо с панели Unreal Editor.",
    ),
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-028", weight=4, impact="HIGH_VALUE",
        question="Есть ли валидатор ассетов в редакторе (Data Validation Subsystem)?",
        tokens=["UEditorValidator", "ValidateData", "AssetValidation"],
        actionable_insight="Автоматическая проверка неверных настроек ассетов перед сборкой проекта.",
    ),
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-029", weight=4, impact="HIGH_VALUE",
        question="Поддерживаются ли кастомные визуализаторы компонентов во viewport (Component Visualizers)?",
        tokens=["FComponentVisualizer", "DrawVisualization", "ViewportDraw"],
        actionable_insight="Наглядная отрисовка радиусов и путей прямо в 3D окне редактора.",
    ),
    CommercialQuestion(
        domain="EDITOR_EUW", question_id="COM-030", weight=4, impact="HIGH_VALUE",
        question="Есть ли автоматическая генерация отчетов по объектам прямо из окна редактора?",
        tokens=["GenerateReport", "ExportStats", "EditorReport"],
        actionable_insight="Полезно для лидов разработки при проведении аудита ресурсов проекта.",
    ),

    # ── 6. ONBOARDING & PLUG-AND-PLAY DEMO MAPS (6 Questions) ─────────────────
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-031", weight=5, impact="HIGH_VALUE",
        question="Содержит ли плагин готовую демо-карту (`/Content/Maps/Demo.umap`) для проверки за 3 минуты?",
        tokens=["Demo", "Example", "Map", "Content", "Sample", "umap"],
        actionable_insight="Снижает процент возвратов на Fab Marketplace на 60% и генерирует отзывы 5 звезд.",
    ),
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-032", weight=4, impact="HIGH_VALUE",
        question="Включена ли подробная документация с пошаговыми инструкциями по установке?",
        tokens=["README", "Doc", "Tutorial", "Guide", "Wiki", "pdf"],
        actionable_insight="Подробный гайд экономит часы работы техподдержки.",
    ),
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-033", weight=4, impact="HIGH_VALUE",
        question="Есть ли видео-туториалы на YouTube или GIF-демонстрации основных фич?",
        tokens=["Video", "YouTube", "GIF", "Overview", "Walkthrough"],
        actionable_insight="Наличие видео в описании листинга увеличивает конверсию в покупку на 40%.",
    ),
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-034", weight=4, impact="HIGH_VALUE",
        question="Поставляются ли готовые пресеты ассетов, которые можно сразу перетащить на сцену?",
        tokens=["Prefab", "Preset", "Asset", "Content", "ReadyToUse"],
        actionable_insight="Принцип 'Drag & Drop' очень ценится начинающими разработчиками.",
    ),
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-035", weight=4, impact="HIGH_VALUE",
        question="Есть ли интерактивное обучение или всплывающие подсказки при первом запуске?",
        tokens=["InteractiveTutorial", "WelcomeWizard", "FirstStartGuide"],
        actionable_insight="Быстрый ввод в работу создает отличный первый опыт использования плагина.",
    ),
    CommercialQuestion(
        domain="ONBOARDING", question_id="COM-036", weight=4, impact="HIGH_VALUE",
        question="Предоставляется ли чек-лист интеграции плагина в существующий проект?",
        tokens=["Checklist", "IntegrationGuide", "MigrationSteps"],
        actionable_insight="Помогает внедрить плагин в уже готовый проект без слома существующей логики.",
    ),

    # ── 7. TECHNICAL ARTIST PRESETS & MATERIAL SYSTEMS (6 Questions) ──────────
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-037", weight=5, impact="HIGH_VALUE",
        question="Включены ли готовые шейдеры и материальные инстансы (Material Instances)?",
        tokens=["Material", "MaterialInstance", "Shader", "HLSL", "PBR"],
        actionable_insight="Привлекает технических художников, ищущих готовые визуальные эффекты.",
    ),
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-038", weight=4, impact="HIGH_VALUE",
        question="Поддерживается ли динамическая смена параметров материалов во время игры (MID)?",
        tokens=["UMaterialInstanceDynamic", "SetScalarParameterValue", "VectorParameter"],
        actionable_insight="Позволяет создавать плавно меняющиеся визуальные эффекты в реальном времени.",
    ),
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-039", weight=4, impact="HIGH_VALUE",
        question="Есть ли поддержка визуальных эффектов Niagara / Cascade?",
        tokens=["Niagara", "Cascade", "ParticleSystem", "VFX"],
        actionable_insight="Готовые эффекты частиц повышают визуальное качество любого игрового проекта.",
    ),
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-040", weight=4, impact="HIGH_VALUE",
        question="Оптимизированы ли шейдеры под мобильные GPU и VR шлемы (Low Shader Complexity)?",
        tokens=["MobileShader", "ShaderComplexity", "LowPoly", "OptimizeShader"],
        actionable_insight="Высокая производительность шейдеров критична для мобильных и VR игр.",
    ),
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-041", weight=4, impact="HIGH_VALUE",
        question="Поддерживается ли процедурная генерация материалов и текстур?",
        tokens=["Procedural", "Substance", "RuntimeTexture", "GenerateTexture"],
        actionable_insight="Процедурность экономит память и дает бесконечное разнообразие визуала.",
    ),
    CommercialQuestion(
        domain="ARTIST_PRESETS", question_id="COM-042", weight=4, impact="HIGH_VALUE",
        question="Включена ли поддержка Lumen и Nanite для UE5 проектов нового поколения?",
        tokens=["Lumen", "Nanite", "VirtualShadowMaps", "UE5Features"],
        actionable_insight="Тег 'UE5 Lumen & Nanite Ready' — обязательное условие для современных продаж.",
    ),

    # ── 8. SUPPORT OVERHEAD & VERSION PORTING FRICTION (6 Questions) ───────────
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-043", weight=5, impact="HIGH_VALUE",
        question="Является ли плагин самодостаточным модулем без тяжелых внешних сторонних зависимостей?",
        tokens=["Standalone", "SelfContained", "NoDependencies", "Independent"],
        actionable_insight="Минимизирует вопросы покупателей по сложной настройке внешних библиотек.",
    ),
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-044", weight=4, impact="RISK",
        question="Зависит ли плагин от приватных внутренних заголовков движка (Private Headers)?",
        tokens=["Private/", "Internal/", "UnrealEngine/Private"],
        actionable_insight="Приватные заголовки ломаются при каждом обновлении UE 5.x, создавая работу по переписыванию.",
    ),
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-045", weight=4, impact="HIGH_VALUE",
        question="Есть ли автоматическое тестирование работоспособности плагина (Automation Spec / Tests)?",
        tokens=["IMPLEMENT_SIMPLE_AUTOMATION_TEST", "AutomationTest", "TestSpec"],
        actionable_insight="Тесты гарантируют быстрый и безболезненный перенос плагина на новые версии UE.",
    ),
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-046", weight=4, impact="HIGH_VALUE",
        question="Выведены ли все информационные сообщения в стандартный лог UE (`UE_LOG`)?",
        tokens=["UE_LOG", "LogTemp", "LogVerbosity", "CustomLogCategory"],
        actionable_insight="Помогает покупателям самостоятельно диагностировать проблемы по логам.",
    ),
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-047", weight=4, impact="HIGH_VALUE",
        question="Предоставляется ли гайд по решению типовых ошибок интеграции (Troubleshooting Guide)?",
        tokens=["Troubleshooting", "FAQ", "KnownIssues", "CommonErrors"],
        actionable_insight="Раздел FAQ в документации снижает поток однотипных вопросов в саппорт на 50%.",
    ),
    CommercialQuestion(
        domain="SUPPORT", question_id="COM-048", weight=4, impact="HIGH_VALUE",
        question="Есть ли поддержка обратной совместимости при обновлении структуры сохранения плагина?",
        tokens=["Serialize", "VersionCheck", "SaveVersion", "MigrateData"],
        actionable_insight="Предотвращает потерю данных у покупателей при выходе новой версии плагина.",
    ),

    # ── 9. EPIC FAB MARKETPLACE EULA & LEGAL SAFETY (6 Questions) ─────────────
    CommercialQuestion(
        domain="LEGAL", question_id="COM-049", weight=5, impact="HIGH_VALUE",
        question="Соответствует ли плагин правилам и EULA маркетплейса Epic Fab?",
        tokens=["LICENSE", "Fab", "Marketplace", "Copyright", "EULA", "EpicGames"],
        actionable_insight="Гарантирует прохождение быстрой модерации при публикации на маркетплейсе.",
    ),
    CommercialQuestion(
        domain="LEGAL", question_id="COM-050", weight=5, impact="RISK",
        question="Есть ли риск заражения коммерческих игр лицензией GPL/AGPL (Copyleft Risk)?",
        tokens=["GPL", "AGPL", "General Public License", "Copyleft"],
        actionable_insight="Удалите GPL код, иначе коммерческие студии отказываются от использования плагина.",
    ),
    CommercialQuestion(
        domain="LEGAL", question_id="COM-051", weight=4, impact="HIGH_VALUE",
        question="Используются ли открытые пермиссивные лицензии для сторонних библиотек (MIT / Apache / BSD)?",
        tokens=["MIT", "Apache", "BSD", "Permissive"],
        actionable_insight="Пермиссивные лицензии полностью безопасны для использования в коммерческих играх.",
    ),
    CommercialQuestion(
        domain="LEGAL", question_id="COM-052", weight=4, impact="HIGH_VALUE",
        question="Чисты ли авторские права на все включенные графические и звуковые ассеты?",
        tokens=["CC0", "RoyaltyFree", "CustomAsset", "CleanRights"],
        actionable_insight="Защищает автора и покупателей от претензий правообладателей.",
    ),
    CommercialQuestion(
        domain="LEGAL", question_id="COM-053", weight=4, impact="HIGH_VALUE",
        question="Отсутствует ли скрытый сбор персональных данных или незаявленная телеметрия?",
        tokens=["Telemetry", "Analytics", "Privacy", "GDPR", "NoTracking"],
        actionable_insight="Чистота от сбора данных — важное требование для корпоративных клиентов.",
    ),
    CommercialQuestion(
        domain="LEGAL", question_id="COM-054", weight=4, impact="HIGH_VALUE",
        question="Указан ли лицензионный файл в корне каждой папки модуля плагина?",
        tokens=["LICENSE.txt", "License.md", "CopyrightNotice"],
        actionable_insight="Юридическая четкость повышает доверие крупных коммерческих покупателей.",
    ),

    # ── 10. COMMUNITY SOCIAL PROOF & B2B ENTERPRISE UPSELL (6 Questions) ───────
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-055", weight=5, impact="HIGH_VALUE",
        question="Есть ли ссылка на активный Discord сервер или форум поддержки сообщества?",
        tokens=["Discord", "Community", "Support", "Forum", "JoinDiscord"],
        actionable_insight="Сообщество в Discord повышает доверие и дает платформу для допродаж.",
    ),
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-056", weight=4, impact="HIGH_VALUE",
        question="Есть ли публичный RoadMap развития плагина (Trello / GitHub Projects)?",
        tokens=["Roadmap", "Trello", "FutureFeatures", "Planned"],
        actionable_insight="Открытый роадмап показывает покупателям, что проект активно развивается.",
    ),
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-057", weight=4, impact="HIGH_VALUE",
        question="Собираются ли публичные отзывы и кейсы использования в реальных выпущенных играх?",
        tokens=["Showcase", "UsedIn", "GamesMadeWith", "Testimonials"],
        actionable_insight="Демонстрация известных игр, использующих плагин — сильнейший фактор продаж.",
    ),
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-058", weight=4, impact="HIGH_VALUE",
        question="Предлагается ли услуга индивидуальной кастомизации плагина под нужды заказчика?",
        tokens=["CustomDevelopment", "Services", "Freelance", "HireUs"],
        actionable_insight="Услуги кастомизации могут приносить от $2,000 до $10,000 с одного клиента.",
    ),
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-059", weight=4, impact="HIGH_VALUE",
        question="Есть ли реферальная или партнерская программа для блогеров и разработчиков?",
        tokens=["Affiliate", "PartnerProgram", "Referral", "Promote"],
        actionable_insight="Партнерка стимулирует ютуберов делать обзоры на ваш плагин.",
    ),
    CommercialQuestion(
        domain="COMMUNITY", question_id="COM-060", weight=4, impact="HIGH_VALUE",
        question="Опубликованы ли исходники примера интеграционного проекта на GitHub?",
        tokens=["SampleProject", "GitHubRepo", "DemoRepository"],
        actionable_insight="Готовый открытый пример проекта позволяет покупателю оценить плагин до покупки.",
    ),
]


def audit_unreal_commercial(root: Path, idx: IndexStoreAdapter) -> list[CommercialQuestion]:
    """Scan Unreal Engine plugin for 60+ commercial, business, UX, and non-technical metrics."""
    for q in COMMERCIAL_QUESTIONS:
        hits = set()

        if q.question_id == "COM-031":
            demo_maps = list(root.rglob("*.umap")) + list(root.rglob("*Demo*")) + list(root.rglob("*Example*"))
            if demo_maps:
                hits.update(str(f.relative_to(root)) for f in demo_maps[:4])

        if q.question_id == "COM-032":
            docs = list(root.glob("*.md")) + list(root.rglob("*.md")) + list(root.rglob("*.txt"))
            if docs:
                hits.update(str(f.relative_to(root)) for f in docs[:4])

        for token in q.tokens:
            try:
                res = idx.search_code(token, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("Binaries", "Intermediate", "Saved", ".git")):
                        hits.add(r.path)
            except Exception:
                pass

        q.evidence = sorted(list(hits))[:4]
        q.found = len(q.evidence) > 0

    return COMMERCIAL_QUESTIONS


def calculate_commercial_score(questions: list[CommercialQuestion]) -> tuple[int, str, str]:
    """Calculate Commercial Readiness Score (0-100) and Publisher Grade."""
    total_weight = sum(q.weight for q in questions)
    found_weight = sum(q.weight for q in questions if q.found)

    score = int((found_weight / total_weight) * 100) if total_weight > 0 else 0

    if score >= 85:
        grade = "A+ (Fab Marketplace Commercial Hit — Turnkey Bestseller)"
        status = "🟢 HIGH COMMERCIAL POTENTIAL — Ready for Fab Release & Studio Sales"
    elif score >= 70:
        grade = "A (Solid Commercial Product)"
        status = "🟢 GOOD — Clear Market Fit & Low Support Overhead"
    elif score >= 55:
        grade = "B (Moderate Commercial Potential)"
        status = "🟡 MEDIUM — Requires Better Onboarding & Blueprint UX"
    else:
        grade = "C/F (Low Publisher Readiness)"
        status = "🔴 LOW — Niche Utility or Onboarding Barrier"

    return score, grade, status


def print_report(project: str, root: Path, questions: list[CommercialQuestion],
    """Documentation for print_report."""
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [q for q in questions if q.found]
    score, grade, status = calculate_commercial_score(questions)

    lines = [
        f"# 💼 Commercial, Business & UX Publisher Audit 3.0 (60Q) — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Commercial & Publisher Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **Commercial Readiness Score** | **{score} / 100** |",
        f"| **Publisher Grade** | **{grade}** |",
        f"| **Commercial Status** | **{status}** |",
        f"| Total Commercial Questions Audited | {len(questions)} |",
        f"| Verified Commercial Signals | {len(found)} |",
        "",
        "## 🔍 Verified Non-Technical Commercial Questions & Evidence",
        "",
        "| Domain | Commercial Question | Status | Verified Code Evidence | Publisher Action |",
        "|---|---|---|---|---|",
    ]

    for q in found:
        ev = ", ".join(f"`{e}`" for e in q.evidence[:2])
        lines.append(f"| `{q.domain}` | {q.question} | ✅ FOUND | {ev} | {q.actionable_insight} |")

    lines += [
        "",
        "## 🚀 Commercial Scaling & Publisher Strategy Blueprint",
        "",
        "1. **Monetization Structure**: Keep Core plugin open-source on GitHub, sell Pro version with C++ Source on Epic Fab for $79-$149.",
        "2. **Designer Accessibility**: Expand Blueprint nodes for non-programmer game designers (BlueprintCallable).",
        "3. **Demo Onboarding**: Package 1-click Demo Level Map in `/Content/Maps/Demo.umap` to minimize buyer refund rates.",
        "4. **Enterprise Tier**: Sell Direct B2B Custom Support Contracts ($999/yr) to AAA studios & Virtual Production teams.",
        "",
        "---",
        f"*Unreal Engine Commercial & Business Publisher Auditor 3.0 · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  💼 UNREAL ENGINE COMMERCIAL & BUSINESS PUBLISHER AUDITOR 3.0 (60Q): {project}")
    print(SEP)
    print(f"  Files indexed                 : {stats.get('total_files', 0):,}")
    print(f"  Commercial Readiness Score    : {score} / 100")
    print(f"  Publisher Grade               : {grade}")
    print(f"  Total Commercial Questions    : {len(questions)}")
    print(f"  Verified Commercial Signals   : {len(found)}")
    print(f"  Audit Speed                   : {elapsed:.3f}s")
    print(f"  Report Saved                  : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    """Documentation for main."""
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/unreal_commercial_audit.py /path/to/ue_plugin [PluginName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"unreal_commercial_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    questions = audit_unreal_commercial(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, questions, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
