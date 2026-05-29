import random
import math
import copy
from packing_solver import evaluate_solution

class Individual:
    def __init__(self, num_items):
        self.order = list(range(num_items))
        random.shuffle(self.order)
        self.rotations = [random.randint(0, 5) for _ in range(num_items)]
        # Araç seçim tercihleri (0: A-01, 1: A-02, 2: A-03, 3: A-04)
        # Her yeni araç açıldığında hangi araç tipinin tercih edileceğini belirtir.
        self.bin_choices = [random.randint(0, 3) for _ in range(num_items)]
        self.fitness = float('inf')
        self.bins = []

    def clone(self):
        new_ind = Individual(len(self.order))
        new_ind.order = list(self.order)
        new_ind.rotations = list(self.rotations)
        new_ind.bin_choices = list(self.bin_choices)
        new_ind.fitness = self.fitness
        new_ind.bins = [b.clone() for b in self.bins]
        return new_ind


def crossover_pmx(parent1, parent2):
    """
    Sıralama (Permutasyon) için Kısmi Eşlemeli Çaprazlama (Partially Mapped Crossover - PMX).
    """
    size = len(parent1)
    cx_point1 = random.randint(0, size - 2)
    cx_point2 = random.randint(cx_point1 + 1, size - 1)
    
    child1 = [-1] * size
    child2 = [-1] * size
    
    # Kesit kopyala
    child1[cx_point1:cx_point2+1] = parent1[cx_point1:cx_point2+1]
    child2[cx_point1:cx_point2+1] = parent2[cx_point1:cx_point2+1]
    
    # Eşlemeleri yap
    for i in range(cx_point1, cx_point2 + 1):
        # Child 1 için eşleme
        val = parent2[i]
        if val not in child1:
            curr = val
            idx = parent2.index(parent1[parent2.index(curr)])
            while child1[idx] != -1:
                idx = parent2.index(parent1[idx])
            child1[idx] = val
            
        # Child 2 için eşleme
        val = parent1[i]
        if val not in child2:
            curr = val
            idx = parent1.index(parent2[parent1.index(curr)])
            while child2[idx] != -1:
                idx = parent1.index(parent2[idx])
            child2[idx] = val
            
    # Kalan boşlukları doldur
    for i in range(size):
        if child1[i] == -1:
            child1[i] = parent2[i]
        if child2[i] == -1:
            child2[i] = parent1[i]
            
    return child1, child2


def crossover_individuals(p1, p2):
    """
    İki bireyi çaprazlayarak yeni iki çocuk oluşturur.
    """
    num_items = len(p1.order)
    c1 = Individual(num_items)
    c2 = Individual(num_items)
    
    # 1. Koli sırası için PMX çaprazlama
    c1.order, c2.order = crossover_pmx(p1.order, p2.order)
    
    # 2. Döndürmeler için tek noktalı çaprazlama
    cx_pt = random.randint(1, num_items - 1)
    c1.rotations = p1.rotations[:cx_pt] + p2.rotations[cx_pt:]
    c2.rotations = p2.rotations[:cx_pt] + p1.rotations[cx_pt:]
    
    # 3. Araç seçimleri için tek noktalı çaprazlama
    cx_pt_b = random.randint(1, num_items - 1)
    c1.bin_choices = p1.bin_choices[:cx_pt_b] + p2.bin_choices[cx_pt_b:]
    c2.bin_choices = p2.bin_choices[:cx_pt_b] + p1.bin_choices[cx_pt_b:]
    
    return c1, c2


def mutate_individual(ind, mutation_rate=0.1):
    """
    Bireyi mutasyona uğratır (Swap mutasyonu, Rotasyon mutasyonu, Araç tercihi mutasyonu).
    """
    num_items = len(ind.order)
    
    # 1. Koli Sırası Mutasyonu: Swap (İki kolinin sırasını değiştir)
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(num_items), 2)
        ind.order[idx1], ind.order[idx2] = ind.order[idx2], ind.order[idx1]
        
    # 2. Döndürme Mutasyonu
    for i in range(num_items):
        if random.random() < mutation_rate:
            ind.rotations[i] = random.randint(0, 5)
            
    # 3. Araç Tercih Mutasyonu
    for i in range(num_items):
        if random.random() < mutation_rate:
            ind.bin_choices[i] = random.randint(0, 3)


def run_genetic_algorithm(items, vehicle_templates, pop_size=30, generations=50, 
                           crossover_rate=0.8, mutation_rate=0.1, tournament_size=3,
                           w1=0.6, w2=0.4):
    """
    Genetik Algoritma çözücüsü.
    Generator olarak yazılmıştır; her nesilde en iyi bireyi yield eder.
    Bu sayede Streamlit arayüzünde canlı grafik çizdirilebilir.
    """
    num_items = len(items)
    population = [Individual(num_items) for _ in range(pop_size)]
    
    # Akıllı Başlangıç (Heuristic Injection):
    # GA'nın yerel minimuma (Büyük Araç) takılmasını önlemek için 
    # popülasyonun ilk bireyine "Büyükten Küçüğe" (First-Fit Decreasing) koli dizilimi veriyoruz.
    # Ayrıca araç tercihi olarak hep Orta (1) veya Küçük (0) denemesini sağlıyoruz.
    if pop_size > 0:
        items_with_idx = list(enumerate(items))
        items_with_idx.sort(key=lambda x: x[1].volume, reverse=True)
        population[0].order = [x[0] for x in items_with_idx]
        population[0].bin_choices = [1] * num_items  # Orta Araç zorlaması
        
    # İlk popülasyonu değerlendir
    for ind in population:
        seq = [items[idx] for idx in ind.order]
        ind.bins, ind.fitness = evaluate_solution(
            seq, ind.rotations, ind.bin_choices, vehicle_templates, w1, w2
        )
        
    # En iyiyi bul
    population.sort(key=lambda x: x.fitness)
    best_ind = population[0].clone()
    
    yield 0, best_ind, [ind.fitness for ind in population]
    
    for gen in range(1, generations + 1):
        new_pop = []
        
        # Elitizm (En iyi 2 bireyi doğrudan yeni nesle aktar)
        new_pop.append(population[0].clone())
        new_pop.append(population[1].clone())
        
        # Popülasyonu doldurana kadar devam et
        while len(new_pop) < pop_size:
            # Turnuva Seçimi
            def tournament_select():
                candidates = random.sample(population, tournament_size)
                candidates.sort(key=lambda x: x.fitness)
                return candidates[0]
                
            p1 = tournament_select()
            p2 = tournament_select()
            
            c1 = p1.clone()
            c2 = p2.clone()
            
            # Çaprazlama
            if random.random() < crossover_rate:
                c1, c2 = crossover_individuals(p1, p2)
                
            # Mutasyon
            mutate_individual(c1, mutation_rate)
            mutate_individual(c2, mutation_rate)
            
            # Değerlendir
            seq1 = [items[idx] for idx in c1.order]
            c1.bins, c1.fitness = evaluate_solution(
                seq1, c1.rotations, c1.bin_choices, vehicle_templates, w1, w2
            )
            
            seq2 = [items[idx] for idx in c2.order]
            c2.bins, c2.fitness = evaluate_solution(
                seq2, c2.rotations, c2.bin_choices, vehicle_templates, w1, w2
            )
            
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)
                
        # Yeni nesle geç
        population = new_pop
        population.sort(key=lambda x: x.fitness)
        
        if population[0].fitness < best_ind.fitness:
            best_ind = population[0].clone()
            
        yield gen, best_ind, [ind.fitness for ind in population]


def run_whale_optimization_algorithm(items, vehicle_templates, pop_size=30, max_iter=50,
                                     w1=0.6, w2=0.4, b=1.0):
    """
    Balina Sürü Optimizasyonu (Whale Optimization Algorithm - WOA) Çözücüsü.
    Generator olarak yazılmıştır; her iterasyonda en iyi balinayı yield eder.
    Bu sayede Streamlit arayüzünde canlı grafik çizdirilebilir.
    """
    num_items = len(items)
    
    # 1. Popülasyon oluştur (Arama ajanları / Balinalar)
    population = [Individual(num_items) for _ in range(pop_size)]
    
    # İlk popülasyonu değerlendir
    for ind in population:
        seq = [items[i] for i in ind.order]
        ind.bins, ind.fitness = evaluate_solution(
            seq, ind.rotations, ind.bin_choices, vehicle_templates, w1, w2
        )
        
    # En iyi balinayı (X*) bul
    population.sort(key=lambda x: x.fitness)
    best_whale = population[0].clone()
    
    yield 0, best_whale, [ind.fitness for ind in population]
    
    # İterasyonlar (Evrimsel süreç)
    for t in range(1, max_iter + 1):
        # a katsayısı doğrusal olarak 2.0'dan 0.0'a azalır
        a = 2.0 - 2.0 * (t / max_iter)
        
        for i in range(pop_size):
            p = random.random()
            r = random.random()
            
            # Katsayı vektörlerini hesapla
            A = 2.0 * a * r - a
            
            current_whale = population[i].clone()
            
            if p < 0.5:
                if abs(A) < 1:
                    # 1. Avı Kuşatma (Encircling Prey): En iyi balinaya (X*) doğru hareket
                    # Lider ile crossover yap
                    current_whale.order, _ = crossover_pmx(current_whale.order, best_whale.order)
                    # Yönelim ve araç tercihlerini liderden kopyala
                    for j in range(num_items):
                        if random.random() < 0.5:
                            current_whale.rotations[j] = best_whale.rotations[j]
                        if random.random() < 0.5:
                            current_whale.bin_choices[j] = best_whale.bin_choices[j]
                else:
                    # 2. Av Arama (Search for Prey): Rastgele bir balinaya (X_rand) doğru hareket
                    rand_whale = random.choice(population)
                    current_whale.order, _ = crossover_pmx(current_whale.order, rand_whale.order)
                    for j in range(num_items):
                        if random.random() < 0.5:
                            current_whale.rotations[j] = rand_whale.rotations[j]
                        if random.random() < 0.5:
                            current_whale.bin_choices[j] = rand_whale.bin_choices[j]
            else:
                # 3. Kabarcık Ağı Saldırısı (Bubble-net Attack): Spiral Güncelleme
                # Lider etrafında helezon (spiral) çizerek arama yap
                # Helezon genişliği liderle olan Hamming Mesafesi (mismatch sayısı) ile orantılıdır
                dist = 0
                for j in range(num_items):
                    if current_whale.order[j] != best_whale.order[j]:
                        dist += 1
                    if current_whale.rotations[j] != best_whale.rotations[j]:
                        dist += 1
                
                # Helezon adımı: liderin etrafında dist katsayısı ve spiral katsayısı (b) ile orantılı miktarda mutasyon uygula
                mutation_intensity = max(1, int(dist * 0.15 * b))
                
                spiral_candidate = best_whale.clone()
                for _ in range(mutation_intensity):
                    # Koli sırasında swap/reinsert
                    if random.random() < 0.6:
                        idx1, idx2 = random.sample(range(num_items), 2)
                        spiral_candidate.order[idx1], spiral_candidate.order[idx2] = spiral_candidate.order[idx2], spiral_candidate.order[idx1]
                    else:
                        idx1 = random.randint(0, num_items - 1)
                        idx2 = random.randint(0, num_items - 1)
                        val = spiral_candidate.order.pop(idx1)
                        spiral_candidate.order.insert(idx2, val)
                    
                    # Rotasyonlarda ve bin tercihlerinde ufak değişimler
                    idx_rot = random.randint(0, num_items - 1)
                    spiral_candidate.rotations[idx_rot] = random.randint(0, 5)
                    idx_bin = random.randint(0, num_items - 1)
                    spiral_candidate.bin_choices[idx_bin] = random.randint(0, 3)
                    
                current_whale = spiral_candidate
                
            # Yeni balinayı değerlendir
            seq = [items[idx] for idx in current_whale.order]
            current_whale.bins, current_whale.fitness = evaluate_solution(
                seq, current_whale.rotations, current_whale.bin_choices, vehicle_templates, w1, w2
            )
            
            # Greedy seçim: Balina durumunu sadece daha iyiye giderse güncelle
            if current_whale.fitness < population[i].fitness:
                population[i] = current_whale
                
        # Popülasyonu sırala ve en iyi balinayı güncelle
        population.sort(key=lambda x: x.fitness)
        if population[0].fitness < best_whale.fitness:
            best_whale = population[0].clone()
            
        yield t, best_whale, [ind.fitness for ind in population]
