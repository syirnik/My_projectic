# integrated_n
import time
import random
from cybersecurity import CyberSecuritySystem, SimulatedAttacks
from neural_network import AdvancedTrafficAI
class IntegratedTrafficSystem:
    """Объединенная система: нейросеть + кибербезопасность"""
    
    def __init__(self):
        # Инициализация нейросети (твой код)
        self.traffic_ai = AdvancedTrafficAI()
        
        # Инициализация безопасности 
        self.security_system = CyberSecuritySystem()
        self.attack_simulator = SimulatedAttacks()
        
        # Статистика
        self.normal_cycles = 0
        self.attack_cycles = 0
        self.blocked_attacks = 0
        
        print("🤖 ИНТЕГРИРОВАННАЯ СИСТЕМА ЗАПУЩЕНА")
        print("   Нейросеть трафика + Система кибербезопасности")
        print("   Режим: Анализ трафика с периодическими кибератаками")
    
    def run_integrated_cycle(self):
        """Один цикл работы объединенной системы"""
        # С вероятностью 30% запускаем кибератаку
        attack_scenario = self.attack_simulator.generate_attack(chance=0.3)
        
        if attack_scenario:
            self.attack_cycles += 1
            return self._handle_cyber_attack(attack_scenario)
        else:
            self.normal_cycles += 1
            return self._handle_normal_traffic()
    
    def _handle_normal_traffic(self):
        print(f"\n ЦИКЛ #{self.normal_cycles + self.attack_cycles}: АНАЛИЗ ТРАФИКА")
        print("   Сканирование пешеходов и транспортных средств...")
        
        all_camera_data = {}
        for camera_pos in self.traffic_ai.camera_system.camera_positions:  # ← БЕЗ .keys()
            all_camera_data[camera_pos] = self.traffic_ai.camera_system.simulate_camera_view(
                camera_pos, self.traffic_ai.traffic_light_state
            )
        
        decision, duration, analysis = self.traffic_ai.make_decision(all_camera_data)
        
        # Имитация легитимного запроса к системе
        legitimate_request = {
            "ip_address": "192.168.1.100",
            "token": list(self.security_system.authentication.authorized_tokens.keys())[0],
            "command": "traffic_analysis", 
            "user_agent": "TrafficAI/1.0",
            "required_permission": "basic_control"
        }
        
        # Проверка безопасности (должна пройти успешно)
        security_check = self.security_system.authenticate_request(**legitimate_request)
        
        print(f"   Решение по трафику: {decision}")
        print(f"   Длительность: {duration} сек")
        print(f"   Безопасность: {security_check['message']}")
        
        return {
            "cycle_type": "traffic_analysis",
            "traffic_decision": decision,
            "duration": duration,
            "security_status": security_check,
            "message": "Нормальный режим работы"
        }
    
    def _handle_cyber_attack(self, attack_scenario):
        """Режим отражения кибератаки"""
        print(f"\n🛡️ ЦИКЛ #{self.normal_cycles + self.attack_cycles}: ОБНАРУЖЕНА КИБЕРАТАКА!")
        print(f"   Тип атаки: {attack_scenario['name']}")
        print(f"   Описание: {attack_scenario['description']}")
        
        blocked_count = 0
        total_requests = 0
        
        # Обработка атаки в зависимости от типа
        if attack_scenario["type"] == "ddos_flood":
            print("   Обнаружены массовые запросы...")
            for request in attack_scenario["requests"]:
                total_requests += 1
                result = self.security_system.authenticate_request(
                    ip_address=request["ip_address"],
                    token=request["token"],
                    command=request["command"],
                    user_agent=request["user_agent"]
                )
                if not result["authenticated"]:
                    blocked_count += 1
        
        else:  # brute_force, sql_injection, reconnaissance
            if "attempts" in attack_scenario:
                requests = attack_scenario["attempts"]
            else:
                requests = [attack_scenario["attack_data"]]
                
            for request in requests:
                total_requests += 1
                result = self.security_system.authenticate_request(
                    ip_address=request["ip_address"],
                    token=request["token"], 
                    command=request["command"],
                    user_agent=request["user_agent"]
                )
                if not result["authenticated"]:
                    blocked_count += 1
        
        self.blocked_attacks += blocked_count
        
        # Нейросеть продолжает работать в фоне
        all_camera_data = {}
        for camera_pos in self.traffic_ai.camera_system.camera_positions:
            all_camera_data[camera_pos] = self.traffic_ai.camera_system.simulate_camera_view(
                camera_pos, self.traffic_ai.traffic_light_state
            )
        
        decision, duration, analysis = self.traffic_ai.make_decision(all_camera_data)
        
        # Вывод результатов защиты
        success_rate = (blocked_count / total_requests) * 100 if total_requests > 0 else 0
        print(f"   Результат защиты: {blocked_count}/{total_requests} запросов заблокировано")
        print(f"   Эффективность: {success_rate:.1f}%")
        print(f"   Решение по трафику: {decision}")
        
        return {
            "cycle_type": "cyber_defense",
            "attack_type": attack_scenario["name"],
            "blocked_requests": blocked_count,
            "total_requests": total_requests,
            "traffic_decision": decision,
            "defense_success": success_rate > 90,
            "message": f"Отражено {blocked_count}/{total_requests} атак"
        }
    
    def get_system_stats(self):
        """Статистика работы системы"""
        total_cycles = self.normal_cycles + self.attack_cycles
        
        return {
            "total_cycles": total_cycles,
            "traffic_analysis_cycles": self.normal_cycles,
            "cyber_defense_cycles": self.attack_cycles,
            "blocked_attacks": self.blocked_attacks,
            "security_status": self.security_system.get_security_status()
        }

# Запуск integrated системы
def main():
    system = IntegratedTrafficSystem()
    
    print("\n" + "="*60)
    print("ЗАПУСК ИНТЕГРИРОВАННОЙ СИСТЕМЫ")
    print("="*60)
    
    # Запускаем 15 циклов
    for i in range(15):
        result: dict = system.run_integrated_cycle()
        
        # Короткая пауза между циклами
        time.sleep(2)
    
    # Финальная статистика
    stats = system.get_system_stats()
    print("\n" + "="*60)
    print("ФИНАЛЬНАЯ СТАТИСТИКА СИСТЕМЫ:")
    print("="*60)
    print(f"Всего циклов работы: {stats['total_cycles']}")
    print(f"Циклов анализа трафика: {stats['traffic_analysis_cycles']}")
    print(f"Циклов отражения атак: {stats['cyber_defense_cycles']}")
    print(f"Всего заблокировано атак: {stats['blocked_attacks']}")
    print(f"Эффективность системы: {(stats['traffic_analysis_cycles'] / stats['total_cycles']) * 100:.1f}%")
    print("="*60)

if __name__ == "__main__":
    main()
    system = IntegratedTrafficSystem()
