# cybersecurity.py
"""
ПОЛНАЯ СИСТЕМА КИБЕРБЕЗОПАСНОСТИ
Защита от DDoS, аутентификация, шифрование, мониторинг угроз
"""
# cybersecurity.py



import numpy as np 
import random
import time
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque

class DDoSProtection:
    """Защита от DDoS-атак с детектированием паттернов"""
    
    def __init__(self):
        self.request_log = defaultdict(deque)
        self.blocked_ips = {}
        self.suspicious_ips = {}
        
        # Настройки защиты
        self.rate_limits = {
            "normal": 50,      # запросов в минуту
            "suspicious": 20,  # для подозрительных IP
            "critical": 10     # для критических команд
        }
        self.block_time = 300  # 5 минут блокировки
        self.analysis_window = 60  # окно анализа в секундах
        
    def check_request(self, ip_address, request_type, user_agent=""):
        """Проверяет запрос на DDoS и подозрительную активность"""
        current_time = time.time()
        
        # Очистка старых данных
        self._clean_old_requests(current_time)
        
        # Проверка блокировки
        if self._is_ip_blocked(ip_address, current_time):
            return {
                "allowed": False, 
                "message": "IP временно заблокирован за подозрительную активность",
                "threat_level": "high"
            }
        
        # Логирование запроса
        request_data = {
            "time": current_time,
            "type": request_type,
            "user_agent": user_agent,
            "size": len(str(request_type)) + len(user_agent)
        }
        self.request_log[ip_address].append(request_data)
        
        # Анализ угроз
        threat_analysis = self._analyze_threat_patterns(ip_address, current_time)
        
        if threat_analysis["threat_level"] == "critical":
            self.blocked_ips[ip_address] = current_time + self.block_time
            return {
                "allowed": False,
                "message": f"Обнаружена {threat_analysis['attack_type']} атака! IP заблокирован",
                "threat_level": "critical"
            }
        elif threat_analysis["threat_level"] == "high":
            self.suspicious_ips[ip_address] = current_time + 600  # 10 минут наблюдения
            return {
                "allowed": False,
                "message": "Подозрительная активность обнаружена",
                "threat_level": "high"
            }
        
        # Проверка лимитов запросов
        limit_check = self._check_rate_limits(ip_address, current_time, request_type)
        if not limit_check["allowed"]:
            return limit_check
        
        return {
            "allowed": True,
            "message": "OK",
            "threat_level": "low"
        }
    
    def _analyze_threat_patterns(self, ip_address, current_time):
        """Анализирует паттерны атак"""
        requests = list(self.request_log[ip_address])
        
        if len(requests) < 5:
            return {"threat_level": "low", "attack_type": None}
        
        # Анализ временных паттернов
        timestamps = [req["time"] for req in requests]
        recent_requests = [req for req in requests if current_time - req["time"] < 30]
        
        # Детектирование флуд-атаки
        if len(recent_requests) > 50:
            return {"threat_level": "critical", "attack_type": "флуд-атака"}
        
        # Детектирование ботнета (равномерные запросы)
        if len(requests) > 10:
            time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            if len(time_diffs) > 5:
                avg_diff = np.mean(time_diffs)
                std_diff = np.std(time_diffs)
                
                if std_diff < 0.05:  # Слишком равномерно
                    return {"threat_level": "critical", "attack_type": "ботнет"}
        
        # Детектирование сканирования уязвимостей
        unique_commands = len(set(req["type"] for req in requests))
        if unique_commands > 15 and len(requests) > 20:
            return {"threat_level": "high", "attack_type": "сканирование"}
        
        return {"threat_level": "low", "attack_type": None}
    
    def _check_rate_limits(self, ip_address, current_time, request_type):
        """Проверяет ограничения частоты запросов"""
        # Определяем лимит в зависимости от типа IP и команды
        if ip_address in self.suspicious_ips:
            rate_limit = self.rate_limits["suspicious"]
        elif request_type in ["system_shutdown", "config_change"]:
            rate_limit = self.rate_limits["critical"]
        else:
            rate_limit = self.rate_limits["normal"]
        
        # Подсчет запросов за последнюю минуту
        recent_requests = [
            req for req in self.request_log[ip_address] 
            if current_time - req["time"] < 60
        ]
        
        if len(recent_requests) > rate_limit:
            self.blocked_ips[ip_address] = current_time + self.block_time
            return {
                "allowed": False,
                "message": f"Превышен лимит запросов: {len(recent_requests)}/{rate_limit}",
                "threat_level": "high"
            }
        
        return {"allowed": True}
    
    def _is_ip_blocked(self, ip_address, current_time):
        """Проверяет блокировку IP"""
        if ip_address in self.blocked_ips:
            if current_time < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
                if ip_address in self.suspicious_ips:
                    del self.suspicious_ips[ip_address]
        return False
    
    def _clean_old_requests(self, current_time):
        """Очищает старые записи"""
        for ip in list(self.request_log.keys()):
            self.request_log[ip] = deque(
                req for req in self.request_log[ip] 
                if current_time - req["time"] < 300
            )
            if not self.request_log[ip]:
                del self.request_log[ip]

class AuthenticationSystem:
    """Система аутентификации с JWT токенами и ролевой моделью"""
    
    def __init__(self):
        self.authorized_tokens = {}
        self.revoked_tokens = set()
        self.failed_attempts = defaultdict(int)
        self.user_roles = {}
        
        # Инициализация системных учетных записей
        self._initialize_system_accounts()
    
    def _initialize_system_accounts(self):
        """Создает системные учетные записи"""
        system_users = {
            "traffic_control": {
                "role": "admin",
                "permissions": ["full_control", "system_config", "basic_control"],
                "token": self._generate_token("traffic_control")
            },
            "emergency_services": {
                "role": "emergency", 
                "permissions": ["priority_override", "emergency_stop"],
                "token": self._generate_token("emergency_services")
            },
            "maintenance": {
                "role": "maintenance",
                "permissions": ["status_check", "basic_control"],
                "token": self._generate_token("maintenance")
            }
        }
        
        for username, data in system_users.items():
            self.authorized_tokens[data["token"]] = {
                "username": username,
                "role": data["role"],
                "permissions": data["permissions"],
                "created": datetime.now(),
                "expires": datetime.now() + timedelta(days=30)
            }
            self.user_roles[username] = data["role"]
    
    def _generate_token(self, username):
        """Генерирует безопасный JWT-токен"""
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": username,
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(days=30)).timestamp(),
            "iss": "traffic_control_system"
        }
        
        # В реальной системе здесь была бы криптография
        header_b64 = secrets.token_urlsafe(16)
        payload_b64 = secrets.token_urlsafe(32)
        signature = secrets.token_urlsafe(16)
        
        return f"{header_b64}.{payload_b64}.{signature}"
    
    def verify_token(self, token, required_permission=None):
        """Проверяет токен и разрешения"""
        # Проверка отозванных токенов
        if token in self.revoked_tokens:
            return {
                "valid": False, 
                "reason": "Токен отозван",
                "threat_level": "medium"
            }
        
        # Проверка блокировки из-за неудачных попыток
        if self.failed_attempts[token] > 5:
            return {
                "valid": False,
                "reason": "Токен заблокирован из-за подозрительной активности", 
                "threat_level": "high"
            }
        
        # Проверка существования токена
        if token not in self.authorized_tokens:
            self.failed_attempts[token] += 1
            return {
                "valid": False,
                "reason": "Недействительный токен",
                "threat_level": "medium"
            }
        
        token_data = self.authorized_tokens[token]
        
        # Проверка срока действия
        if datetime.now() > token_data["expires"]:
            self.revoked_tokens.add(token)
            return {
                "valid": False,
                "reason": "Срок действия токена истек",
                "threat_level": "low"
            }
        
        # Проверка разрешений
        if required_permission and required_permission not in token_data["permissions"]:
            return {
                "valid": False,
                "reason": f"Недостаточно прав: требуется {required_permission}",
                "threat_level": "medium"
            }
        
        # Сброс счетчика неудачных попыток при успешной аутентификации
        self.failed_attempts[token] = 0
        
        return {
            "valid": True,
            "username": token_data["username"],
            "role": token_data["role"],
            "permissions": token_data["permissions"]
        }
    
    def revoke_token(self, token):
        """Отзывает токен"""
        self.revoked_tokens.add(token)
        if token in self.authorized_tokens:
            del self.authorized_tokens[token]

class EncryptionSystem:
    """Система шифрования и целостности данных"""
    
    def __init__(self):
        self.encryption_key = secrets.token_bytes(32)
        self.hmac_key = secrets.token_bytes(32)
        
    def encrypt_data(self, data):
        """Шифрует данные с использованием AES-256 (упрощенная версия)"""
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        
        # В реальной системе здесь был бы AES-256-GCM
        # Для демонстрации используем HMAC + хеширование
        data_bytes = data.encode('utf-8')
        
        # HMAC для целостности
        hmac = hashlib.pbkdf2_hmac(
            'sha256', 
            data_bytes, 
            self.hmac_key, 
            100000
        ).hex()
        
        # "Шифрование" (в реальности - AES)
        encrypted = hashlib.sha256(data_bytes + self.encryption_key).hexdigest()
        
        return {
            "encrypted_data": encrypted,
            "hmac": hmac,
            "timestamp": datetime.now().isoformat()
        }
    
    def verify_integrity(self, encrypted_package, original_data=None):
        """Проверяет целостность данных"""
        try:
            # Проверка HMAC
            if original_data:
                data_bytes = original_data.encode('utf-8') if isinstance(original_data, str) else original_data
                expected_hmac = hashlib.pbkdf2_hmac(
                    'sha256', data_bytes, self.hmac_key, 100000
                ).hex()
                
                if encrypted_package["hmac"] != expected_hmac:
                    return False, "Нарушена целостность данных"
            
            # Проверка временной метки (защита от replay-атак)
            package_time = datetime.fromisoformat(encrypted_package["timestamp"])
            if datetime.now() - package_time > timedelta(minutes=5):
                return False, "Данные устарели"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Ошибка проверки: {str(e)}"
    
    def decrypt_data(self, encrypted_package, expected_original=None):
        """Расшифровывает данные и проверяет целостность"""
        integrity_ok, message = self.verify_integrity(encrypted_package, expected_original)
        if not integrity_ok:
            return None, message
        
        # В реальной системе здесь было бы AES-расшифрование
        # Для демонстрации возвращаем исходные данные
        return expected_original, "OK"

class ThreatIntelligence:
    """Система анализа и классификации угроз"""
    
    def __init__(self):
        self.threat_database = self._load_threat_database()
        self.behavioral_patterns = {}
        
    def _load_threat_database(self):
        """Загружает базу известных угроз"""
        return {
            "ip_reputation": {
                "185.165.0.0/16": "known_botnet",
                "45.155.0.0/16": "scanner_network", 
                "192.168.666.0/24": "internal_testing"
            },
            "malicious_patterns": [
                "sql_injection",
                "xss_attempt", 
                "command_injection",
                "path_traversal"
            ],
            "suspicious_user_agents": [
                "nikto", "sqlmap", "metasploit", "nmap"
            ]
        }
    
    def analyze_request(self, ip_address, user_agent, request_data):
        """Анализирует запрос на предмет угроз"""
        threat_score = 0
        detected_threats = []
        
        # Проверка репутации IP
        ip_threat = self.threat_database["ip_reputation"].get(ip_address)
        if ip_threat:
            threat_score += 30
            detected_threats.append(f"IP с плохой репутацией: {ip_threat}")
        
        # Анализ User-Agent
        if any(agent in user_agent.lower() for agent in self.threat_database["suspicious_user_agents"]):
            threat_score += 25
            detected_threats.append("Обнаружен сканер уязвимостей")
        
        # Поиск вредоносных паттернов в данных
        request_str = str(request_data).lower()
        for pattern in self.threat_database["malicious_patterns"]:
            if pattern in request_str:
                threat_score += 40
                detected_threats.append(f"Обнаружен {pattern}")
        
        # Определение уровня угрозы
        if threat_score >= 70:
            threat_level = "critical"
        elif threat_score >= 40:
            threat_level = "high" 
        elif threat_score >= 20:
            threat_level = "medium"
        else:
            threat_level = "low"
        
        return {
            "threat_level": threat_level,
            "threat_score": threat_score,
            "detected_threats": detected_threats,
            "recommendation": self._get_recommendation(threat_level)
        }
    
    def _get_recommendation(self, threat_level):
        """Возвращает рекомендации по обработке угрозы"""
        recommendations = {
            "critical": "Немедленная блокировка и оповещение",
            "high": "Блокировка и детальный анализ",
            "medium": "Усиленное наблюдение", 
            "low": "Стандартный мониторинг"
        }
        return recommendations.get(threat_level, "Неизвестный уровень угрозы")

class SecurityMonitor:
    """Мониторинг безопасности и реагирование на инциденты"""
    
    def __init__(self):
        self.security_events = deque(maxlen=1000)
        self.alert_rules = self._load_alert_rules()
        self.incident_counter = 0
        
    def _load_alert_rules(self):
        """Загружает правила генерации оповещений"""
        return {
            "multiple_failures": {
                "threshold": 5,
                "time_window": 60,
                "severity": "high"
            },
            "ddos_detected": {
                "threshold": 1, 
                "time_window": 1,
                "severity": "critical"
            },
            "suspicious_activity": {
                "threshold": 3,
                "time_window": 300,
                "severity": "medium"
            }
        }
    
    def log_security_event(self, event_type, details, severity="low"):
        """Логирует событие безопасности"""
        event = {
            "id": self.incident_counter,
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "severity": severity,
            "ip": details.get("ip_address", "unknown"),
            "action_taken": details.get("action", "logged")
        }
        
        self.security_events.append(event)
        self.incident_counter += 1
        
        # Проверка правил оповещений
        alert = self._check_alert_rules(event_type, severity)
        if alert:
            self._trigger_alert(alert, event)
        
        return event["id"]
    
    def _check_alert_rules(self, event_type, severity):
        """Проверяет правила генерации оповещений"""
        if event_type == "authentication_failure":
            recent_failures = [
                event for event in self.security_events 
                if event["type"] == "authentication_failure" 
                and datetime.now() - datetime.fromisoformat(event["timestamp"]) < timedelta(seconds=60)
            ]
            if len(recent_failures) >= self.alert_rules["multiple_failures"]["threshold"]:
                return {
                    "type": "multiple_authentication_failures",
                    "severity": "high",
                    "message": f"Обнаружено {len(recent_failures)} неудачных попыток входа за 60 секунд"
                }
        
        return None
    
    def _trigger_alert(self, alert, event):
        """Активирует оповещение безопасности"""
        print(f"🚨 СИГНАЛИЗАЦИЯ БЕЗОПАСНОСТИ: {alert['message']}")
        print(f"   Событие: {event}")
        print(f"   Рекомендуемое действие: {self._get_incident_response(alert['severity'])}")
    
    def _get_incident_response(self, severity):
        """Возвращает план реагирования на инциденты"""
        responses = {
            "critical": "Немедленная изоляция системы, оповещение ИБ-команды",
            "high": "Блокировка источника, усиленный мониторинг, анализ логов",
            "medium": "Детальный анализ, обновление правил фильтрации",
            "low": "Стандартный мониторинг, запись в лог"
        }
        return responses.get(severity, "Неизвестный уровень серьезности")
    
    def get_security_report(self):
        """Генерирует отчет о безопасности"""
        recent_events = list(self.security_events)[-50:]  # Последние 50 событий
        
        severity_counts = defaultdict(int)
        for event in recent_events:
            severity_counts[event["severity"]] += 1
        
        return {
            "total_events": len(recent_events),
            "severity_distribution": dict(severity_counts),
            "recent_incidents": recent_events[-10:],  # Последние 10 инцидентов
            "report_time": datetime.now().isoformat()
        }

class CyberSecuritySystem:
    """ГЛАВНАЯ СИСТЕМА КИБЕРБЕЗОПАСНОСТИ - интегрирует все компоненты"""
    
    def __init__(self):
        self.ddos_protection = DDoSProtection()
        self.authentication = AuthenticationSystem()
        self.encryption = EncryptionSystem()
        self.threat_intel = ThreatIntelligence()
        self.monitor = SecurityMonitor()
        
        print("Система кибербезопасности инициализирована")
        print("Компоненты: DDoS защита, Аутентификация, Шифрование, Мониторинг")
    
    def authenticate_request(self, ip_address, token, command, user_agent="", required_permission=None):
        """Полный цикл аутентификации и проверки безопасности"""
        
        # 1. Проверка DDoS и базовой безопасности
        ddos_check = self.ddos_protection.check_request(ip_address, command, user_agent)
        if not ddos_check["allowed"]:
            self.monitor.log_security_event(
                "ddos_protection_block",
                {
                    "ip_address": ip_address,
                    "reason": ddos_check["message"],
                    "threat_level": ddos_check["threat_level"],
                    "action": "blocked"
                },
                ddos_check["threat_level"]
            )
            return {
                "authenticated": False,
                "message": ddos_check["message"],
                "threat_level": ddos_check["threat_level"]
            }
        
        # 2. Анализ угроз
        threat_analysis = self.threat_intel.analyze_request(ip_address, user_agent, command)
        if threat_analysis["threat_level"] in ["high", "critical"]:
            self.monitor.log_security_event(
                "threat_detected",
                {
                    "ip_address": ip_address,
                    "threats": threat_analysis["detected_threats"],
                    "threat_score": threat_analysis["threat_score"],
                    "action": "blocked"
                },
                threat_analysis["threat_level"]
            )
            return {
                "authenticated": False,
                "message": f"Обнаружены угрозы: {', '.join(threat_analysis['detected_threats'])}",
                "threat_level": threat_analysis["threat_level"]
            }
        
        # 3. Аутентификация
        auth_check = self.authentication.verify_token(token, required_permission)
        if not auth_check["valid"]:
            self.monitor.log_security_event(
                "authentication_failure",
                {
                    "ip_address": ip_address,
                    "reason": auth_check["reason"],
                    "threat_level": auth_check.get("threat_level", "medium"),
                    "action": "logged"
                },
                auth_check.get("threat_level", "medium")
            )
            return {
                "authenticated": False,
                "message": auth_check["reason"],
                "threat_level": auth_check.get("threat_level", "medium")
            }
        
        # 4. Шифрование лога для аудита
        audit_data = {
            "ip": ip_address,
            "user": auth_check["username"],
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "threat_analysis": threat_analysis
        }
        encrypted_audit = self.encryption.encrypt_data(audit_data)
        
        # 5. Логирование успешного доступа
        self.monitor.log_security_event(
            "successful_access",
            {
                "ip_address": ip_address,
                "username": auth_check["username"],
                "role": auth_check["role"],
                "command": command,
                "action": "allowed"
            },
            "low"
        )
        
        return {
            "authenticated": True,
            "message": "Доступ разрешен",
            "username": auth_check["username"],
            "role": auth_check["role"],
            "permissions": auth_check["permissions"],
            "encrypted_audit": encrypted_audit,
            "threat_level": "low"
        }
    
    def get_security_status(self):
        """Возвращает текущий статус безопасности"""
        return {
            "ddos_protection": {
                "blocked_ips": len(self.ddos_protection.blocked_ips),
                "suspicious_ips": len(self.ddos_protection.suspicious_ips)
            },
            "authentication": {
                "active_tokens": len(self.authentication.authorized_tokens),
                "revoked_tokens": len(self.authentication.revoked_tokens)
            },
            "monitoring": self.monitor.get_security_report()
        }
# ... остальной код cybersecurity.py ...

class SimulatedAttacks:
    """Генератор искусственных кибератак для тестирования системы"""
    
    def __init__(self):
        self.attack_scenarios = {
            "ddos_flood": {
                "name": "DDoS флуд-атака",
                "description": "Массовые запросы с ботнета",
                "ip_range": ["185.165.1.{}", "45.155.2.{}"],
                "requests_per_second": 20,
                "duration": 5
            },
            "brute_force": {
                "name": "Подбор учетных данных", 
                "description": "Множественные неудачные попытки входа",
                "fake_tokens": ["invalid_token_", "hack_attempt_"],
                "attempts_per_minute": 10
            },
            "sql_injection": {
                "name": "SQL инъекция", 
                "description": "Попытка внедрения вредоносного кода",
                "patterns": ["' OR '1'='1", "DROP TABLE", "UNION SELECT"],
                "target_commands": ["get_config", "system_status"]
            }
        }
        
        self.attack_active = False
        self.current_attack = None
    
    def generate_attack(self, chance=0.3):
        """С вероятностью chance запускает случайную атаку"""
        if random.random() < chance and not self.attack_active:
            attack_type = random.choice(list(self.attack_scenarios.keys()))
            self.current_attack = self.attack_scenarios[attack_type]
            self.attack_active = True
            return self._execute_attack(attack_type)
        return None
    
    def _execute_attack(self, attack_type):
        """Выполняет конкретный сценарий атаки"""
        scenario = self.attack_scenarios[attack_type]
        
        if attack_type == "ddos_flood":
            return self._simulate_ddos(scenario)
        elif attack_type == "brute_force":
            return self._simulate_brute_force(scenario)
        elif attack_type == "sql_injection":
            return self._simulate_sql_injection(scenario)
    
    def _simulate_ddos(self, scenario):
        attack_requests = []
        base_ip = random.choice(scenario["ip_range"])
        
        for i in range(scenario["requests_per_second"]):
            ip = base_ip.format(random.randint(1, 255))
            attack_requests.append({
                "ip_address": ip,
                "command": "system_status",
                "user_agent": "Mozilla/5.0 (compatible; Botnet)",
                "token": "invalid"
            })
        
        return {
            "type": "ddos_flood",
            "name": scenario["name"],
            "description": scenario["description"],
            "requests": attack_requests,
            "duration": scenario["duration"]
        }
    
    def _simulate_brute_force(self, scenario):
        """Имитирует подбор учетных данных"""
        attempts = []
        base_token = random.choice(scenario["fake_tokens"])
        
        for i in range(scenario["attempts_per_minute"]):
            attempts.append({
                "ip_address": f"192.168.1.{random.randint(100, 200)}",
                "command": "traffic_control",
                "user_agent": "Mozilla/5.0",
                "token": base_token + str(random.randint(1000, 9999))
            })
        
        return {
            "type": "brute_force", 
            "name": scenario["name"],
            "description": scenario["description"],
            "attempts": attempts
        }
    
    def _simulate_sql_injection(self, scenario):
        """Имитирует SQL инъекцию"""
        pattern = random.choice(scenario["patterns"])
        command = random.choice(scenario["target_commands"])
        
        return {
            "type": "sql_injection",
            "name": scenario["name"],
            "description": scenario["description"],
            "attack_data": {
                "ip_address": f"10.0.1.{random.randint(50, 150)}",
                "command": f"{command}{pattern}",
                "user_agent": "Mozilla/5.0 (HackTool)",
                "token": "admin' OR '1'='1"
            }
        }

# ОБЯЗАТЕЛЬНО добавить SimulatedAttacks в экспорт!
__all__ = ['CyberSecuritySystem', 'DDoSProtection', 'AuthenticationSystem', 
           'EncryptionSystem', 'ThreatIntelligence', 'SecurityMonitor', 'SimulatedAttacks']
