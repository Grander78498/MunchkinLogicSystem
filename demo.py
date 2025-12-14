#!/usr/bin/env python3
"""
Демонстрация работы логического языка на трёх проблемных ситуациях
"""

from repl import REPL

def run_demo():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         ДЕМОНСТРАЦИЯ ЛОГИЧЕСКОГО ЯЗЫКА ПРОГРАММИРОВАНИЯ          ║
║                  Практическая работа №1 ПСППР                    ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    situations = [
        ("examples/situation1.shldn", "Нормальная ситуация"),
        ("examples/situation2.shldn", "Установка целевого значения"),
        ("examples/situation3.shldn", "Противоречивые условия"),
    ]
    
    for i, (filename, description) in enumerate(situations, 1):
        print(f"\n{'='*70}")
        print(f"СИТУАЦИЯ {i}: {description}")
        print(f"{'='*70}\n")
        
        repl = REPL()
        repl.cmd_load(filename)
        
        input("\nНажмите Enter для продолжения...")
    
    print("\n✓ Демонстрация завершена")

if __name__ == "__main__":
    run_demo()