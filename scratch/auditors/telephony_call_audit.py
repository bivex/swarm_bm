#!/usr/bin/env python3
"""
╔═════════════════════════════════════════════════════════════════════════╗
║   📞 Telephony & Voice AI Codebase Auditor & M&A Flipping Evaluator     ║
║     10 Specialized Telecom/AI Engineers · Legacy to Modern AI Voice     ║
╚═════════════════════════════════════════════════════════════════════════╝

Evaluates legacy telephony, IVR, call center, or WebRTC codebases for:
1. Legacy stack detection (Python 2/3.6, Asterisk AMI/AGI, C++ SIP, PHP IVR)
2. Upgrade path to Modern AI Voice Agents (OpenAI Realtime, LiveKit, Deepgram, ElevenLabs)
3. M&A Flipping & Resale Value Estimation (Refactoring Effort vs Valuation Boost)

Usage:
    python3 scratch/telephony_call_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

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
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


# ─────────────────────────────────────────────────────────────────────
# 10 Telephony & Voice AI Audit Specialists
# ─────────────────────────────────────────────────────────────────────
@dataclass
class TelecomSpecialist:
    name: str
    role: str
    emoji: str
    focus: str
    # Questions: (question, search_tokens, risk_weight 1-3)
    questions: list[tuple[str, list[str], int]]


TELECOM_TEAM: list[TelecomSpecialist] = [

    TelecomSpecialist(
        name="Dr. Alexey Morozov", role="Voice AI & LLM Architect", emoji="🎙️",
        focus="IVR Modernization & Real-Time AI Voice Agent Migration",
        questions=[
            ("Есть ли поддержка современных Voice AI (LiveKit, Daily, OpenAI Realtime API)?",
             ["livekit", "daily", "openai", "realtime", "voice_agent", "llm", "pipecat", "vocode"], 3),
            ("Какая STT (Speech-to-Text) система используется (Whisper, Deepgram, Vosk, Google)?",
             ["whisper", "deepgram", "vosk", "stt", "speech_to_text", "transcribe", "recognize", "asr"], 2),
            ("Какая TTS (Text-to-Speech) система используется (ElevenLabs, Cartesia, Piper)?",
             ["elevenlabs", "cartesia", "piper", "tts", "text_to_speech", "synthesize", "polly", "coqui"], 2),
            ("Реализован ли Barge-in (перебивание бота голосом клиента в реальном времени)?",
             ["barge_in", "interrupt", "silence", "vad", "voice_activity", "cancel_speech", "break"], 3),
            ("Используется ли VAD (Voice Activity Detection, например Silero VAD)?",
             ["vad", "silero", "webrtcvad", "speech_detected", "voice_detected", "silence_threshold"], 2),
            ("Какая задержка (latency) у текущей голосовой логики? Есть ли стриминг аудио?",
             ["stream", "chunk", "ws", "websocket", "latency", "buffer", "frame", "20ms"], 3),
            ("Есть ли интеграция с внешними LLM для ведения диалога (LangChain, LlamaIndex, Raw Prompt)?",
             ["prompt", "completion", "chat", "llm", "langchain", "tools", "function_call", "system_prompt"], 2),
            ("Сохраняется ли контекст звонка и история диалога (Conversation Memory)?",
             ["conversation", "memory", "history", "messages", "context", "transcript", "turns"], 2),
        ]
    ),

    TelecomSpecialist(
        name="Marcus Vance", role="SIP & WebRTC Core Engineer", emoji="📞",
        focus="Core Signaling, Media Engines & Telecom Protocols",
        questions=[
            ("Какие SIP/VoIP движки используются (Asterisk, FreeSWITCH, Kamailio, OpenSIPS)?",
             ["asterisk", "freeswitch", "kamailio", "opensips", "pjsip", "sofia", "sip", "ami", "ari"], 3),
            ("Есть ли поддержка WebRTC (pion, mediasoup, Janus, libwebrtc)?",
             ["webrtc", "pion", "mediasoup", "janus", "peerconnection", "sdp", "ice", "candidate"], 3),
            ("Каким образом передаётся медиа-поток (RTP/SRTP, WebSockets, gRPC)?",
             ["rtp", "srtp", "socket", "websocket", "udp", "rtp_packet", "payload_type"], 2),
            ("Какие аудио-кодеки поддерживаются (Opus, G.711 PCMU/PCMA, G.722, AMR)?",
             ["opus", "g711", "pcmu", "pcma", "g722", "amr", "codec", "sample_rate", "8000", "16000"], 2),
            ("Используются ли CPaaS провайдеры (Twilio, Telnyx, Plivo, Bandwidth)?",
             ["twilio", "telnyx", "plivo", "bandwidth", "signalwire", "voximplant", "agora"], 2),
            ("Установлен ли ICE/STUN/TURN сервер для прохождения NAT?",
             ["turn", "stun", "coturn", "ice_servers", "credential", "relay", "nat"], 2),
            ("Есть ли обработка SIP заголовков и статус-кодов (4xx, 5xx, 6xx, BYE, INVITE)?",
             ["INVITE", "BYE", "ACK", "CANCEL", "SIP/2.0", "header", "call_id", "from_tag", "to_tag"], 2),
            ("Поддерживается ли DTMF ввод (тональный набор 0-9, *, #)?",
             ["dtmf", "rfc2833", "inband", "sip_info", "digits", "digit", "keypress"], 1),
        ]
    ),

    TelecomSpecialist(
        name="Viktor Lindqvist", role="Real-Time Media Pipeline Specialist", emoji="⚡",
        focus="Ultra-Low Latency & High-Concurrency Audio Streaming",
        questions=[
            ("Насколько низок jitter и размер аудио-буферов (целевая задержка < 300мс)?",
             ["buffer", "jitter", "queue", "frame_size", "chunk_size", "latency", "delay", "ring_buffer"], 3),
            ("Используется ли асинхронный I/O для медиа-потоков (asyncio, Tokio, Go routines)?",
             ["asyncio", "tokio", "goroutine", "epoll", "event_loop", "select", "nonblocking"], 3),
            ("Как устроена обработка параллельных звонков (concurrency capacity)?",
             ["channel", "concurrency", "max_calls", "call_limit", "worker_pool", "concurrent_calls"], 3),
            ("Есть ли эхоподавление (AEC) и шумогашение (Noise Suppression)?",
             ["aec", "echo_cancellation", "noise_suppression", "ns", "agc", "filter", "denoise"], 2),
            ("Используется ли Redis Streams / NATS / gRPC для передача аудио межу сервисами?",
             ["redis", "nats", "grpc", "stream", "pubsub", "channel", "queue", "broadcast"], 2),
            ("Как происходит ресемплинг аудио (например 8kHz PSTN <-> 16kHz/48kHz AI)?",
             ["resample", "sox", "ffmpeg", "samplerate", "converter", "downsample", "upsample"], 2),
            ("Есть ли утечки памяти или файловых дескрипторов при частых звонках?",
             ["close", "free", "destroy", "leak", "dispose", "cleanup", "hangup", "disconnect"], 3),
            ("Как управляется жизненный цикл звонка (State Machine: Dialing -> Connected -> Ended)?",
             ["state", "status", "enum", "CONNECTING", "CONNECTED", "DISCONNECTED", "HANGUP", "state_machine"], 2),
        ]
    ),

    TelecomSpecialist(
        name="Helena Vance", role="Telecom Security & Compliance Specialist", emoji="🔐",
        focus="STIR/SHAKEN, DTMF PCI-DSS, Call Recording GDPR & Anti-Fraud",
        questions=[
            ("Зашифрован ли медиа-трафик и сигнализация (SRTP, TLS, SIPS)?",
             ["srtp", "tls", "sips", "crypto", "ssl", "certificate", "key", "encryption"], 3),
            ("Соблюдается ли регуляторика записей звонков (GDPR / HIPAA consent notification)?",
             ["recording_consent", "gdpr", "hipaa", "consent", "privacy", "disclosure", "announcement"], 3),
            ("Есть ли защита от SIP Toll Fraud и несанкционированного SIP-транкинга?",
             ["rate_limit", "auth", "ip_allowlist", "fraud", "unauthorized", "block_ip", "fail2ban"], 3),
            ("Маскируются ли DTMF данные кредитных карт (PCI-DSS DTMF masking)?",
             ["pci", "mask_dtmf", "mute_recording", "sensitive", "dtmf_filter", "card_number"], 2),
            ("Поддерживается ли подпись вызовов STIR/SHAKEN для защиты от подмены номера (Caller ID Spoofing)?",
             ["stir", "shaken", "attestation", "identity", "caller_id", "passport", "cert"], 2),
            ("Безопасно ли хранятся API ключи CPaaS провайдеров (Twilio Auth Token, SIP Passwords)?",
             ["TWILIO_AUTH_TOKEN", "SIP_PASSWORD", "secret", "env", "vault", "credentials"], 3),
            ("Есть ли защита от DoS/DDoS атак на SIP порты (5060 UDP/TCP)?",
             ["fail2ban", "iptables", "rate_limit", "max_contacts", "ddos", "flood", "firewall"], 2),
            ("Как маскируются PII данные в логах звонков и транскриптах?",
             ["redact", "mask", "pii", "anonymize", "log_filter", "sensitive_data"], 2),
        ]
    ),

    TelecomSpecialist(
        name="Dmitry Sokolov", role="Call Data & Audio Storage Architect", emoji="💾",
        focus="CDR (Call Detail Records), Audio Storage & Transcript Indexing",
        questions=[
            ("В каких форматах хранятся аудиозаписи звонков (WAV 8kHz, MP3, OGG, Opus)?",
             ["wav", "mp3", "ogg", "opus", "pcm", "audio_format", "recording_path", "filename"], 1),
            ("Куда загружаются аудиофайлы (AWS S3, MinIO, локальный диск)?",
             ["s3", "minio", "bucket", "upload", "storage", "cloud_storage", "local_path"], 2),
            ("Как устроена база данных CDR (Call Detail Records)?",
             ["cdr", "call_log", "duration", "billsec", "disposition", "caller", "callee", "call_id"], 2),
            ("Используется ли колоночная БД для аналитики звонков (ClickHouse, PostgreSQL)?",
             ["clickhouse", "postgres", "timescale", "bigquery", "analytics", "sql", "table"], 2),
            ("Хранятся ли расшифровки (transcripts) звонков с привязкой по времени (Word Timestamps)?",
             ["transcript", "timestamps", "words", "speaker", "diarization", "utterance", "segment"], 2),
            ("Автоматически ли удаляются старые аудиозаписи по политике retention?",
             ["retention", "ttl", "auto_delete", "cleanup", "cron", "expire", "lifecycle"], 2),
            ("Есть ли поиск по содержимому расшифровок звонков (Full-Text Search)?",
             ["search", "fulltext", "elasticsearch", "pg_trgm", "query", "vector", "embedding"], 2),
            ("Используется ли Diarization (разделение голосов диктора и клиента)?",
             ["diarization", "speaker_id", "channel_0", "channel_1", "stereo", "dual_channel"], 2),
        ]
    ),

    TelecomSpecialist(
        name="Robert Sterling", role="Legacy Telecom Refactoring Lead", emoji="🛠️",
        focus="Legacy Stack Audit, Tech Debt & Modernization Roadmap",
        questions=[
            ("Используются ли устаревшие стеки (Python 2.7, PHP 5/7, C++98, Node 10)?",
             ["python2", "php", "c++98", "legacy", "deprecated", "old", "v1", "historical"], 3),
            ("Завязан ли проект на устаревшие библиотеки Asterisk (AMI/AGI/pystrix/phpagi)?",
             ["ami", "agi", "pystrix", "phpagi", "asterisk-java", "panoramisk", "fastagi"], 3),
            ("Есть ли мокапы и захардкоженные IVR сценарии (Hardcoded Callflows)?",
             ["hardcoded", "switch", "case", "if_dial", "ivr_menu", "goto", "priority", "dialplan"], 2),
            ("Насколько монолитна архитектура? Выделены ли медиа-серверы от бизнес-логики?",
             ["monolith", "tight", "coupled", "all_in_one", "separate", "decoupled", "microservice"], 3),
            ("Каков объём мёртвого/закомментированного кода в телеком логике?",
             ["# TODO", "# FIXME", "/* legacy */", "// deprecated", "unused", "dead_code"], 2),
            ("Используются ли современные асинхронные фреймворки (FastAPI, Go, Rust, Modern Node)?",
             ["fastapi", "gin", "actix", "tokio", "nest", "express", "modern", "async"], 2),
            ("Есть ли тесты для голосовой логики (Mock Call Testing, SIP Stubs)?",
             ["mock_call", "sip_stub", "test_dial", "fake_audio", "pytest", "spec", "telecom_test"], 3),
            ("Насколько просто заменить текущий телеком движок на новый (Abstraction Layer)?",
             ["adapter", "interface", "abstract", "provider", "telecom_engine", "driver", "port"], 3),
        ]
    ),

    TelecomSpecialist(
        name="Sven Lindemann", role="Telecom Infrastructure & Autoscaling SRE", emoji="🚀",
        focus="High Availability, Carrier Trunk Redundancy & Elastic Scaling",
        questions=[
            ("Настроена ли отказоустойчивость SIP трафика (Kamailio / OpenSIPS Load Balancer)?",
             ["kamailio", "opensips", "load_balancer", "failover", "ha", "keepalived", "pacemaker"], 3),
            ("Как происходит авто-масштабирование без разрыва активных звонков (Zero Call Drop Scaling)?",
             ["hpa", "graceful_shutdown", "drain", "active_calls", "drain_node", "autoscaling"], 3),
            ("Есть ли резервирование операторов связи (Carrier Redundancy / Multi-Trunk Failover)?",
             ["trunk", "carrier", "primary_provider", "backup_provider", "failover_route", "outbound_route"], 3),
            ("Используется ли Kubernetes / Helm для развёртывания телеком стека?",
             ["k8s", "kubernetes", "helm", "deployment", "statefulset", "daemonset", "ingress"], 2),
            ("Настроены ли Coturn / TURN серверы в нескольких гео-зонах (Geo-distributed TURN)?",
             ["geo", "region", "turn_cluster", "latency_routing", "closest_node", "edge"], 2),
            ("Как проверяется доступность SIP-транков (OPTIONS Pings / Health Checks)?",
             ["OPTIONS", "ping", "qualify", "keepalive", "trunk_status", "carrier_health"], 2),
            ("Есть ли лимиты на одновременные звонки для защиты серверов от перегрузки?",
             ["max_cps", "max_channels", "limit", "capacity", "queue_overflow", "congestion"], 2),
            ("Как устроен деплой новых версий без прерывания текущих разговоров (Zero-Downtime Deploy)?",
             ["zero_downtime", "canary", "blue_green", "drain_mode", "rolling_update"], 3),
        ]
    ),

    TelecomSpecialist(
        name="Klara Szabo", role="QoS & Call Telemetry Specialist", emoji="📈",
        focus="MOS Score, Packet Loss, Call Drop Rates & Disconnect Reasons",
        questions=[
            ("Измеряется ли качество звука MOS (Mean Opinion Score)?",
             ["mos", "r_factor", "audio_quality", "pesq", "polqa", "qos", "metrics"], 2),
            ("Отслеживаются ли потери пакетов (Packet Loss) и джиттер (Jitter) в реальном времени?",
             ["packet_loss", "jitter", "rtt", "round_trip", "stats", "getStats", "rtp_stats"], 2),
            ("Логируются ли причины завершения вызова (SIP Disconnect Cause Codes 16, 17, 21)?",
             ["cause_code", "hangup_cause", "sip_code", "NORMAL_CLEARING", "USER_BUSY", "NO_ANSWER"], 2),
            ("Используется ли Homer / SIPCAPTURE для полной трассировки SIP пакетов?",
             ["homer", "sipcapture", "hep", "trace", "sip_trace", "wireshark", "pcap"], 2),
            ("Есть ли дашборды для мониторинга активных звонков (Prometheus/Grafana)?",
             ["grafana", "prometheus", "active_calls_gauge", "call_duration_histogram", "metrics"], 2),
            ("Алертит ли система при всплеске сброшенных звонков (Call Drop Rate Spikes)?",
             ["alert", "drop_rate", "threshold", "pagerduty", "slack_notify", "anomaly"], 2),
            ("Отслеживается ли задержка ответа бота (Time-To-First-Audio / Latency Metric)?",
             ["ttfa", "first_audio", "response_time", "latency_ms", "time_to_response"], 3),
            ("Есть ли дашборд операторов / агентов (Agent Status: Available, Busy, Wrap-up)?",
             ["agent_status", "wrap_up", "idle", "busy", "pause", "queue_stats", "dashboard"], 1),
        ]
    ),

    TelecomSpecialist(
        name="Jean-Luc Dubois", role="Telephony Monetization & Billing Specialist", emoji="💰",
        focus="Billing Engines, Rate Cards, Call Metering & BYOC Support",
        questions=[
            ("Как устроена тарификация звонков (посекундная, поминутная, покликовая)?",
             ["billing", "rate", "cost", "price", "duration", "billsec", "per_minute", "charge"], 3),
            ("Поддерживаются ли прайс-листы операторов (Rate Cards / Prefix Pricing)?",
             ["rate_card", "prefix", "country_code", "destination_rate", "cost_per_min", "pricing_table"], 2),
            ("Есть ли поддержка BYOC (Bring Your Own Carrier) для корпоративных клиентов?",
             ["byoc", "custom_trunk", "user_carrier", "sip_trunk_config", "custom_sip"], 3),
            ("Интегрирован ли биллинг с платежными системами (Stripe, Recurly, PayPal)?",
             ["stripe", "recurly", "payment", "invoice", "balance", "top_up", "auto_recharge"], 2),
            ("Есть ли контроль баланса клиента в реальном времени (Prepaid Cut-off upon $0)?",
             ["prepaid", "balance", "credit_limit", "insufficient_funds", "cut_off", "hangup_no_balance"], 3),
            ("Сравниваются ли затраты облачных STT/TTS vs Self-Hosted решений для оптимизации маржи?",
             ["cloud_cost", "margin", "self_hosted", "open_source_tts", "whisper_cpp", "piper"], 2),
            ("Есть ли учет переадресаций и входящих/исходящих каналов (Inbound vs Outbound Billing)?",
             ["inbound_rate", "outbound_rate", "forwarding_cost", "did_cost", "number_rental"], 2),
            ("Генерируются ли закрывающие документы и счета (Invoices, Usage Reports)?",
             ["invoice", "statement", "usage_report", "pdf", "billing_history", "receipt"], 1),
        ]
    ),

    TelecomSpecialist(
        name="Victor K.", role="Voice SaaS M&A Flipping Analyst", emoji="📈",
        focus="Commercial Resale Value, White-Label Readiness & Flipping Margin",
        questions=[
            ("Подготовлен ли проект к White-Label перепродаже (легкая смена бренда/лого/домена)?",
             ["white_label", "branding", "logo", "theme", "tenant_name", "custom_domain", "tenant_logo"], 3),
            ("Легко ли выделить Voice AI логику в отдельный готовый продукт/микросервис?",
             ["standalone", "decoupled", "modular", "api_only", "sdk", "engine_only"], 3),
            ("Оценка привлекательности для покупателей: готовое ли это решение Voice AI Agent?",
             ["voice_bot", "ai_agent", "call_automation", "smart_ivr", "outbound_bot", "inbound_bot"], 3),
            ("Есть ли готовые B2B интеграции с популярными CRM (Bitrix24, amoCRM, Salesforce, HubSpot)?",
             ["crm", "bitrix", "amocrm", "salesforce", "hubspot", "webhook_crm", "lead_creation"], 3),
            ("Насколько полная документация по развёртыванию и настройке телеком стека?",
             ["README", "docs", "telephony_setup", "sip_config", "deployment_guide", "api_docs"], 2),
            ("Есть ли готовый веб-интерфейс управления сценариями звонков (Visual Callflow Builder)?",
             ["builder", "flow", "node", "canvas", "diagram", "block", "visual_editor", "callflow"], 3),
            ("Оценка риска рефакторинга: превышает ли стоимость переделки ценность проекта?",
             ["refactor_effort", "rewrite_cost", "tech_debt_score", "flipping_value", "margin_estimate"], 3),
            ("Готовность к быстрому выходу на рынки США/ЕС (US/EU Telco Standards & Numbers)?",
             ["e164", "country_codes", "us_number", "eu_number", "international", "number_formatting"], 2),
        ]
    ),
]


# ─────────────────────────────────────────────────────────────────────
# Audit Execution & Analysis Engine
# ─────────────────────────────────────────────────────────────────────
def run_telephony_audit(repo_path: Path, project_name: str) -> dict[str, Any]:
    t0 = time.perf_counter()

    print(f"\n{'═'*72}")
    print(f"  📞 TELEPHONY & VOICE AI CODEBASE AUDITOR (Flipping & Modernization)")
    print(f"  📁 Project     : {project_name}")
    print(f"  🗓  Date        : {date.today()}")
    print(f"  📍 Target Path : {repo_path}")
    print(f"{'═'*72}")

    print(f"\n  [*] Building BM25+AST index over telephony codebase...")
    idx = IndexStoreAdapter()
    job = JobEngineAdapter()
    t_idx = time.perf_counter()
    stats = idx.rebuild(repo_path)
    total_files = stats.get("total_files", 0)
    print(f"  [+] Index ready: {total_files:,} files indexed in {(time.perf_counter()-t_idx)*1000:.0f}ms\n")

    team_results: list[dict] = []
    legacy_signals: list[str] = []
    modern_signals: list[str] = []
    all_gaps: list[dict] = []
    answered = 0
    total_questions = sum(len(s.questions) for s in TELECOM_TEAM)

    for spec in TELECOM_TEAM:
        print(f"  {spec.emoji} [{spec.name} · {spec.role}]")
        print(f"     Focus: {spec.focus}")

        spec_findings = []
        spec_found = 0

        for (question, tokens, risk_weight) in spec.questions:
            all_files: dict[str, float] = {}
            all_symbols: list[Any] = []
            seen: set[str] = set()

            for token in tokens:
                hits = idx.search_code(token, limit=4)
                for h in hits:
                    if h.path not in all_files or h.score > all_files[h.path]:
                        all_files[h.path] = h.score

                syms = idx.search_symbols(token, limit=2)
                for s in syms:
                    nm = getattr(s, "name", str(s))
                    if nm not in seen:
                        seen.add(nm)
                        all_symbols.append(s)

            ranked = sorted(all_files.items(), key=lambda x: -x[1])
            top_files = [p for p, _ in ranked[:4]]
            top_syms = all_symbols[:4]

            if top_files or top_syms:
                status = "✅ FOUND"
                spec_found += 1
                answered += 1

                # Track legacy vs modern signals
                if any(t in ["asterisk", "ami", "agi", "phpagi", "python2", "php", "g711", "pcmu"] for t in tokens):
                    legacy_signals.append(f"Legacy Telecom Signal ({tokens[0]}): {top_files[0] if top_files else 'AST'}")
                if any(t in ["livekit", "daily", "openai", "realtime", "whisper", "deepgram", "elevenlabs", "webrtc"] for t in tokens):
                    modern_signals.append(f"Modern Voice AI Signal ({tokens[0]}): {top_files[0] if top_files else 'AST'}")

                short_f = ", ".join(f.split("/")[-1] for f in top_files[:2]) if top_files else "AST Symbol"
                print(f"     {status} {question[:56]:<56} → {short_f}")
            else:
                status = "⚪ MISSING"
                print(f"     {status} {question[:56]}")
                if risk_weight >= 2:
                    all_gaps.append({
                        "specialist": spec.name,
                        "role": spec.role,
                        "question": question,
                        "weight": risk_weight,
                    })

            spec_findings.append({
                "question": question,
                "status": status,
                "weight": risk_weight,
                "files": top_files,
                "symbols": [
                    {"name": getattr(s, "name", str(s)),
                     "kind": getattr(s, "kind", ""),
                     "path": getattr(s, "path", ""),
                     "line": getattr(s, "line", 0)}
                    for s in top_syms
                ]
            })

        cov = (spec_found / len(spec.questions)) * 100
        print(f"     Coverage: {spec_found}/{len(spec.questions)} ({cov:.0f}%)\n")

        team_results.append({
            "name": spec.name,
            "role": spec.role,
            "emoji": spec.emoji,
            "focus": spec.focus,
            "found_count": spec_found,
            "total": len(spec.questions),
            "findings": spec_findings,
        })

    elapsed = time.perf_counter() - t0

    # Calculate Modernization Score
    legacy_count = len(legacy_signals)
    modern_count = len(modern_signals)

    if modern_count > legacy_count * 1.5 and modern_count >= 5:
        stack_tech = "🚀 MODERN VOICE AI (LiveKit / WebRTC / OpenAI Realtime)"
        refactor_tier = "TIER 1 — LOW REFACTORING (Turnkey Product)"
        effort_weeks = "1–2 weeks"
        flipping_multiplier = "3.5x – 5.0x"
    elif modern_count > 0 or legacy_count < 3:
        stack_tech = "🔄 HYBRID TELECOM (Legacy SIP + Modern APIs)"
        refactor_tier = "TIER 2 — MEDIUM REFACTORING (Voice AI Agent Upgrade)"
        effort_weeks = "3–5 weeks"
        flipping_multiplier = "2.0x – 3.5x"
    else:
        stack_tech = "📜 LEGACY TELEPHONY (Asterisk AMI/AGI / Old VoIP / PHP IVR)"
        refactor_tier = "TIER 3 — FULL AI REWORK (Complete Engine Replacement)"
        effort_weeks = "6–10 weeks"
        flipping_multiplier = "1.5x – 2.5x"

    return {
        "project": project_name,
        "repo_path": str(repo_path),
        "date": str(date.today()),
        "total_files": total_files,
        "total_questions": total_questions,
        "answered": answered,
        "coverage_pct": round(answered / total_questions * 100, 1),
        "elapsed_seconds": round(elapsed, 3),
        "stack_tech": stack_tech,
        "refactor_tier": refactor_tier,
        "effort_weeks": effort_weeks,
        "flipping_multiplier": flipping_multiplier,
        "legacy_signals": legacy_signals,
        "modern_signals": modern_signals,
        "all_gaps": sorted(all_gaps, key=lambda x: -x["weight"]),
        "team_results": team_results,
    }


# ─────────────────────────────────────────────────────────────────────
# Report Generator
# ─────────────────────────────────────────────────────────────────────
def generate_telephony_report(res: dict, out_path: Path) -> None:
    lines = []
    a = lines.append

    a(f"# 📞 Telephony & Voice AI Codebase Audit: {res['project']}")
    a(f"> M&A Flipping & Tech Modernization Assessment · {res['date']}")
    a("")

    a("## 📊 Executive Summary & Valuation Metrics")
    a("")
    a("| Parameter | Audit Result |")
    a("|-----------|--------------|")
    a(f"| Project | `{res['project']}` |")
    a(f"| Repository | `{res['repo_path']}` |")
    a(f"| Codebase Files | **{res['total_files']:,}** |")
    a(f"| Telecom Specialists | **{len(TELECOM_TEAM)}** |")
    a(f"| Coverage | **{res['answered']}/{res['total_questions']} ({res['coverage_pct']}%)** |")
    a(f"| Audit Speed | **{res['elapsed_seconds']}s** |")
    a(f"| Detected Stack | **{res['stack_tech']}** |")
    a(f"| Refactoring Category | **{res['refactor_tier']}** |")
    a(f"| Estimated Upgrade Effort | **{res['effort_weeks']}** |")
    a(f"| Potential Resale Multiplier | **{res['flipping_multiplier']}** |")
    a("")

    # Modernization Roadmap
    a("## 🚀 Voice AI Modernization Roadmap (Legacy → High-Value AI Product)")
    a("")
    a("To maximize resale value to enterprise buyers, follow this 4-step upgrade plan:")
    a("")
    a("1. **Core Transport Upgrade (SIP → WebRTC / LiveKit)**")
    a("   - Replace Asterisk AMI/AGI or legacy SIP wrappers with **LiveKit WebRTC** or **Daily.co**.")
    a("   - Target latency: **<200ms audio transport**.")
    a("")
    a("2. **AI Voice Agent Pipeline Integration**")
    a("   - STT: Integrate **Deepgram Nova-2** or **Whisper.cpp** (Streaming WebSocket).")
    a("   - LLM: Integrate **OpenAI Realtime API** or **FastAPI + vLLM / Groq** for ultra-fast response.")
    a("   - TTS: Integrate **Cartesia Sonic** or **ElevenLabs Turbo v2.5**.")
    a("   - VAD: Enable **Silero VAD** for instant **Barge-in** (user interruption).")
    a("")
    a("3. **Compliance & Multi-Tenancy**")
    a("   - Add DTMF PCI-DSS masking, STIR/SHAKEN header verification, and GDPR call recording consent.")
    a("   - Add Multi-tenant SaaS routing (Tenant ID + Custom Carrier BYOC).")
    a("")
    a("4. **Commercial Packaging & CRM Integrations**")
    a("   - Build Visual Callflow Builder (drag-and-drop nodes).")
    a("   - Native webhooks & bi-directional sync for **amoCRM, Bitrix24, Salesforce, HubSpot**.")
    a("")

    # Gaps & Risks
    gaps = res["all_gaps"]
    a("## 🚨 Key Technical Gaps & Modernization Requirements")
    a("")
    if gaps:
        a("| Specialist | Missing Capability / Requirement | Priority |")
        a("|---|---|---|")
        for g in gaps:
            prio = "🔴 CRITICAL" if g["weight"] == 3 else "🟠 HIGH"
            a(f"| {g['specialist']} ({g['role']}) | {g['question']} | {prio} |")
        a("")
    else:
        a("> 🎉 Exceptional result! All key telephony & Voice AI requirements are present in the codebase.\n")

    # Team Breakdown
    a("## 👥 Telecom & Voice AI Specialists Detailed Audit")
    a("")
    for tr in res["team_results"]:
        cov = (tr["found_count"] / tr["total"]) * 100
        bar = "█" * int(cov / 10) + "░" * (10 - int(cov / 10))
        a(f"### {tr['emoji']} {tr['name']} — {tr['role']}")
        a(f"**Focus:** {tr['focus']}")
        a(f"**Coverage:** `{bar}` {tr['found_count']}/{tr['total']} ({cov:.0f}%)")
        a("")
        a("| # | Audit Question | Status | File Hits |")
        a("|---|---|---|---|")
        for i, f in enumerate(tr["findings"], 1):
            st_icon = "✅" if f["status"] == "✅ FOUND" else "⚪"
            f_str = ", ".join(f["files"][:2]) if f["files"] else "—"
            a(f"| {i} | {f['question'][:65]} | {st_icon} | `{f_str[:45]}` |")
        a("")

    # Footer
    a("---")
    a(f"*Audit generated in **{res['elapsed_seconds']}s** by Swarm BM Telephony Engine · {res['date']}*")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [+] Audit Report written → {out_path}")


# ─────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 scratch/telephony_call_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    repo = Path(sys.argv[1]).resolve()
    if not repo.exists():
        print(f"[ERROR] Path not found: {repo}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else repo.name

    res = run_telephony_audit(repo, project_name)

    # Save report artifact
    from pathlib import Path as _P
    app_data = _P.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = project_name.lower().replace(" ", "_").replace("/", "_")
    out = app_data / f"telephony_audit_{safe_name}.md"
    generate_telephony_report(res, out)
