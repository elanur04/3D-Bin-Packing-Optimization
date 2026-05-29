import copy

class Item:
    def __init__(self, item_id, name, depth, height, width):
        """
        Koli Sınıfı.
        depth (D) -> Derinlik (x ekseni boyutu)
        height (Y) -> Yükseklik (y ekseni boyutu)
        width (G) -> Genişlik (z ekseni boyutu)
        """
        self.id = item_id
        self.name = name
        self.d = float(depth)
        self.h = float(height)
        self.w = float(width)
        self.volume = self.d * self.h * self.w
        
        # Yerleşim koordinatları (Sol-Alt-Arka köşe)
        self.x = 0.0  # Derinlik eksenindeki başlangıç konumu
        self.y = 0.0  # Yükseklik eksenindeki başlangıç konumu
        self.z = 0.0  # Genişlik eksenindeki başlangıç konumu
        
        # Aktif yönelim boyutları (Rotation uygulandıktan sonraki d, h, w)
        self.rot_d = self.d
        self.rot_h = self.h
        self.rot_w = self.w
        self.rotation_type = 0  # 0 ile 5 arasında 6 farklı yönelim

    def get_rotations(self):
        """
        Kutunun 90 derecelik döndürmeler altındaki 6 farklı yönelim boyutunu döner.
        Format: (rot_depth, rot_height, rot_width)
        """
        return [
            (self.d, self.h, self.w), # 0: D-Y-G (Normal)
            (self.d, self.w, self.h), # 1: D-G-Y
            (self.h, self.d, self.w), # 2: Y-D-G
            (self.h, self.w, self.d), # 3: Y-G-D
            (self.w, self.d, self.h), # 4: G-D-Y
            (self.w, self.h, self.d)  # 5: G-Y-D
        ]

    def set_rotation(self, rotation_type):
        """
        Kutunun yönelim tipini ayarlar ve aktif boyutlarını günceller.
        """
        rotations = self.get_rotations()
        self.rotation_type = rotation_type % 6
        self.rot_d, self.rot_h, self.rot_w = rotations[self.rotation_type]

    def get_corners(self):
        """
        Kutunun yerleştirildikten sonraki bitiş koordinatlarını döner.
        """
        return (self.x + self.rot_d, self.y + self.rot_h, self.z + self.rot_w)

    def is_overlapping(self, other):
        """
        Başka bir kutu ile 3 boyutlu uzayda çakışıp çakışmadığını kontrol eder.
        AABB (Axis-Aligned Bounding Box) çakışma testi.
        """
        # Eğer bir eksende bile çakışma yoksa, kutular çakışmıyordur.
        if (self.x + self.rot_d <= other.x or other.x + other.rot_d <= self.x):
            return False
        if (self.y + self.rot_h <= other.y or other.y + other.rot_h <= self.y):
            return False
        if (self.z + self.rot_w <= other.z or other.z + other.rot_w <= self.z):
            return False
        return True

    def clone(self):
        """
        Kutunun derin bir kopyasını oluşturur.
        """
        new_item = Item(self.id, self.name, self.d, self.h, self.w)
        new_item.x = self.x
        new_item.y = self.y
        new_item.z = self.z
        new_item.rot_d = self.rot_d
        new_item.rot_h = self.rot_h
        new_item.rot_w = self.rot_w
        new_item.rotation_type = self.rotation_type
        return new_item


class Bin:
    def __init__(self, bin_id, name, depth, height, width):
        """
        Araç (Bin) Sınıfı.
        depth (D) -> Derinlik (x ekseni boyutu)
        height (Y) -> Yükseklik (y ekseni boyutu)
        width (G) -> Genişlik (z ekseni boyutu)
        """
        self.id = bin_id
        self.name = name
        self.d = float(depth)
        self.h = float(height)
        self.w = float(width)
        self.max_volume = self.d * self.h * self.w
        self.packed_items = []
        self.used_volume = 0.0

    @property
    def empty_volume(self):
        return self.max_volume - self.used_volume

    @property
    def utilization_ratio(self):
        """Araç doluluk oranı (0.0 - 1.0)"""
        return self.used_volume / self.max_volume

    @property
    def empty_ratio(self):
        """Araç boşluk oranı (0.0 - 1.0)"""
        return self.empty_volume / self.max_volume

    def can_hold_volume(self, item):
        """Kutunun hacmi araçta kalan boş hacimden küçük mü kontrolü."""
        return self.empty_volume >= item.volume

    def check_dimensions_fit(self, item):
        """Kutunun aktif yönelim boyutları araç boyutlarını aşıyor mu kontrolü."""
        return item.rot_d <= self.d and item.rot_h <= self.h and item.rot_w <= self.w

    def pack_item(self, item, x, y, z):
        """
        Kutuyu verilen koordinata yerleştirir.
        Gerekli hacim ve pozisyon güncellemelerini yapar.
        """
        item_copy = item.clone()
        item_copy.x = x
        item_copy.y = y
        item_copy.z = z
        
        # Araç sınır kontrolü
        if (x + item_copy.rot_d > self.d or 
            y + item_copy.rot_h > self.h or 
            z + item_copy.rot_w > self.w):
            return False
            
        # Çakışma kontrolü
        for packed in self.packed_items:
            if item_copy.is_overlapping(packed):
                return False
                
        self.packed_items.append(item_copy)
        self.used_volume += item_copy.volume
        return True

    def clone(self):
        """Aracın ve içindeki kutuların derin kopyasını döner."""
        new_bin = Bin(self.id, self.name, self.d, self.h, self.w)
        new_bin.packed_items = [item.clone() for item in self.packed_items]
        new_bin.used_volume = self.used_volume
        return new_bin
