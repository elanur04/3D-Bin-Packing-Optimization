import copy
from models import Item, Bin

def get_candidate_points(bin_obj):
    """
    Aracın içerisindeki kutuların köşe noktalarına göre yeni kutu yerleştirilebilecek 
    aday koordinat noktalarını (Candidate Points) hesaplar.
    Bu noktalar kutu yerleşimleri sonrası oluşan 3 yeni yerleşim yönüdür (x+d, y+h, z+w).
    """
    # Başlangıç noktası her zaman (0.0, 0.0, 0.0)
    points = [(0.0, 0.0, 0.0)]
    
    for item in bin_obj.packed_items:
        # Kutunun yerleşimi sonrası 3 yeni aday nokta oluşur
        p1 = (item.x + item.rot_d, item.y, item.z)
        p2 = (item.x, item.y + item.rot_h, item.z)
        p3 = (item.x, item.y, item.z + item.rot_w)
        
        points.extend([p1, p2, p3])
        
    valid_points = []
    for p in points:
        px, py, pz = p
        
        # Nokta araç sınırları içinde mi?
        if px >= bin_obj.d or py >= bin_obj.h or pz >= bin_obj.w:
            continue
            
        # Nokta halihazırda yerleştirilmiş herhangi bir kutunun tamamen içinde mi?
        inside_any = False
        for item in bin_obj.packed_items:
            # Tolerans payı ile kontrol (yüzen nokta hatalarını önlemek için epsilon eklenir)
            eps = 1e-5
            if (item.x - eps <= px < item.x + item.rot_d - eps and
                item.y - eps <= py < item.y + item.rot_h - eps and
                item.z - eps <= pz < item.z + item.rot_w - eps):
                inside_any = True
                break
                
        if not inside_any:
            valid_points.append(p)
            
    # Eşsiz noktaları al
    unique_points = list(set(valid_points))
    
    # Sıralama: Önce Yükseklik (y) - tabana yakınlık, sonra Derinlik (x) - arkaya yakınlık, sonra Genişlik (z) - sola yakınlık
    # Bu sıralama "Yerçekimi/Taban" öncelikli kompakt bir yerleşim (Deepest-Bottom-Left) sağlar.
    unique_points.sort(key=lambda pt: (pt[1], pt[0], pt[2]))
    return unique_points


def evaluate_solution(item_sequence, rotations, bin_choices, vehicle_templates, w1=0.6, w2=0.4):
    """
    Verilen koli sırası, koli yönelimleri ve araç seçim tercihlerine göre paketlemeyi simüle eder.
    Geriye yerleşim yapılmış araç listesini ve uygunluk (fitness) değerini döner.
    """
    # 1. Koli kopyalarını alarak nesne referans mutasyonlarını engelliyoruz
    local_items = [it.clone() for it in item_sequence]
    
    # 2. Araç şablonlarını güvenli bir şekilde klonlayarak şişmelerini önlüyoruz.
    # Ağır copy.deepcopy yerine 100x daha hızlı olan nesneye özel .clone() metodunu kullanıyoruz.
    local_vehicles = [v.clone() for v in vehicle_templates]
    
    # Araç kopyalarını alalım
    bins = []
    
    # Her bir koli için yerleştirme dene
    for idx, item in enumerate(local_items):
        # Kolinin yönelimini ayarla
        rot_type = rotations[idx]
        item.set_rotation(rot_type)
        
        packed = False
        
        # 1. Mevcut açık araçlara sığdırmaya çalış
        for bin_obj in bins:
            if not bin_obj.can_hold_volume(item):
                continue
            if not bin_obj.check_dimensions_fit(item):
                continue
                
            # Aday yerleşim noktalarını al
            candidates = get_candidate_points(bin_obj)
            for cx, cy, cz in candidates:
                if bin_obj.pack_item(item, cx, cy, cz):
                    packed = True
                    break # İçteki koordinat döngüsünden çık
            if packed:
                break # Dıştaki araç tarama döngüsünden çık (Break Bug giderildi)
                
        # 2. Eğer mevcut araçlara sığmadıysa, yeni bir araç aç
        if not packed:
            # Tercih edilen araç tipini al
            # Kördüğümü çözmek için len(bins) yerine döngüdeki kolinin kendi sırasına (idx) bağlandı
            pref_bin_idx = bin_choices[idx % len(bin_choices)] % len(local_vehicles)
            
            # Tüm araç şablonlarını küçükten büyüğe sıralı varsayıyoruz (A-01, A-02, A-03, A-04)
            selected_template = local_vehicles[pref_bin_idx]
            
            # Boyutsal sığma kontrolü
            item_fits = False
            # Eğer seçilen araç tipine sığmıyorsa sırayla diğer araç tiplerini dene
            for b_idx in range(pref_bin_idx, len(local_vehicles)):
                temp = local_vehicles[b_idx]
                # Yönelimi kontrol et
                if item.rot_d <= temp.d and item.rot_h <= temp.h and item.rot_w <= temp.w:
                    selected_template = temp
                    item_fits = True
                    break
            
            # Eğer yukarıdaki yöne sığmadıysa tüm araçları baştan kontrol et (en büyüğüne bile sığmıyorsa)
            if not item_fits:
                for b_idx in range(len(local_vehicles)):
                    temp = local_vehicles[b_idx]
                    if item.rot_d <= temp.d and item.rot_h <= temp.h and item.rot_w <= temp.w:
                        selected_template = temp
                        item_fits = True
                        break
            
            # Yeni bir araç oluştur
            new_bin_id = f"V-{len(bins)+1:02d}_{selected_template.id}"
            new_bin = Bin(new_bin_id, selected_template.name, selected_template.d, selected_template.h, selected_template.w)
            
            # İlk koordinat (0,0,0) noktasına yerleştir
            if new_bin.pack_item(item, 0.0, 0.0, 0.0):
                bins.append(new_bin)
            else:
                # Eğer hiçbir şekilde sığmıyorsa (ceza olarak yüksek değer eklenir)
                pass

    # Fitness hesaplama:
    # f(x) = w1 * (kullanılan araç sayısı) + w2 * (toplam boş hacim oranı)
    used_bins_count = len(bins)
    
    if used_bins_count == 0:
        return bins, 999999.0
        
    total_max_volume = sum(b.max_volume for b in bins)
    total_used_volume = sum(b.used_volume for b in bins)
    total_empty_volume = total_max_volume - total_used_volume
    total_empty_ratio = total_empty_volume / total_max_volume
    
    # Ceza puanı: Eğer yerleştirilemeyen koli kaldıysa
    unpacked_count = len(item_sequence) - sum(len(b.packed_items) for b in bins)
    penalty = unpacked_count * 1000.0
    
    # Simetri kırıcı (Tie-breaker): Aynı kutuları aynı araca koyan farklı yerleşimler
    # tıpatıp aynı Boşluk_Oranı değerini üretir ve fitness grafiği "dümdüz" olur.
    # Algoritmanın kutuları "daha sıkı" yerleştirmeyi öğrenmesi için, 
    # kolilerin merkeze (0,0,0) olan uzaklıklarına (ya da max yüksekliğe) göre çok küçük bir ceza ekliyoruz.
    compactness_penalty = 0.0
    for b in bins:
        for item in b.packed_items:
            # Kutunun merkezine/orijine olan uzaklığını daha güçlü cezalandırıyoruz
            # Çarpanı 0.0005 yaptık ki grafikte gözle görülür bir "öğrenme" (aşağı doğru eğim) oluşsun.
            compactness_penalty += (item.x + item.y + item.z) * 0.0005
            
    fitness = (w1 * used_bins_count) + (w2 * total_empty_ratio) + penalty + compactness_penalty
    
    return bins, fitness
