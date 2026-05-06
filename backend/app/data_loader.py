import pandas as pd
import re
import os


def clean_text(text: str) -> str:
    """Metni temizle: HTML etiketleri, fazla boşluklar, özel karakterler."""
    if not isinstance(text, str):
        return ""
    # HTML etiketlerini kaldır
    text = re.sub(r'<[^>]+>', '', text)
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    # Başındaki ve sonundaki boşlukları kaldır
    text = text.strip()
    return text


def load_and_prepare_data(data_dir: str = "data", max_docs: int = 5000) -> pd.DataFrame:
    """
    Türkçe haber veri kümesini yükle ve hazırla.
    Hugging Face'den indirilmiş CSV veya datasets kütüphanesiyle yüklenir.
    """

    csv_path = os.path.join(data_dir, "turkish_news.csv")

    if os.path.exists(csv_path):
        print(f"Yerel CSV dosyası bulundu: {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        print("Veri kümesi Hugging Face'den indiriliyor...")
        try:
            from datasets import load_dataset
            dataset = load_dataset(
                "anilguven/turkish_news_dataset",
                split="train"
            )
            df = dataset.to_pandas()
            # CSV olarak kaydet (tekrar indirmemek için)
            os.makedirs(data_dir, exist_ok=True)
            df.to_csv(csv_path, index=False)
            print(f"Veri kümesi kaydedildi: {csv_path}")
        except Exception as e:
            print(f"Hugging Face indirme hatası: {e}")
            print("Alternatif veri kümesi deneniyor...")
            try:
                from datasets import load_dataset
                dataset = load_dataset(
                    "serdarakyol/interpress-turkish-news-classification-65k",
                    split="train"
                )
                df = dataset.to_pandas()
                os.makedirs(data_dir, exist_ok=True)
                df.to_csv(csv_path, index=False)
                print(f"Alternatif veri kümesi kaydedildi: {csv_path}")
            except Exception as e2:
                print(f"Alternatif indirme hatası: {e2}")
                print("Örnek veri oluşturuluyor...")
                df = create_sample_data()
                os.makedirs(data_dir, exist_ok=True)
                df.to_csv(csv_path, index=False)

    # Sütun isimlerini standartlaştır
    df = standardize_columns(df)

    # Metinleri temizle
    df['title'] = df['title'].apply(clean_text)
    df['content'] = df['content'].apply(clean_text)

    # Boş satırları kaldır
    df = df.dropna(subset=['title', 'content'])
    df = df[df['title'].str.len() > 5]
    df = df[df['content'].str.len() > 20]

    # Belirtilen sayıda doküman al
    if len(df) > max_docs:
        # Her kategoriden orantılı örnekle
        df = df.groupby('category', group_keys=False).apply(
            lambda x: x.sample(min(len(x), max_docs // df['category'].nunique()),
                               random_state=42)
        )

    # İndeks sıfırla
    df = df.reset_index(drop=True)
    df['id'] = df.index

    print(f"Toplam {len(df)} doküman yüklendi.")
    print(f"Kategoriler: {df['category'].unique().tolist()}")

    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Farklı veri kümelerinin sütun isimlerini standartlaştır."""

    column_mapping = {}

    # Olası başlık sütunları
    for col in ['title', 'Title', 'baslik', 'Baslik', 'headline', 'Headline', 'HABERLER']:
        if col in df.columns:
            column_mapping[col] = 'title'
            break

    # Olası içerik sütunları
    for col in ['content', 'Content', 'text', 'Text', 'icerik', 'Icerik',
                'description', 'Description', 'body', 'Body', 'HABERLER']:
        if col in df.columns and col not in column_mapping:
            column_mapping[col] = 'content'
            break

    # Olası kategori sütunları
    for col in ['category', 'Category', 'kategori', 'Kategori', 'label',
                'Label', 'class', 'Class', 'topic', 'Topic', 'ETIKET']:
        if col in df.columns:
            column_mapping[col] = 'category'
            break

    df = df.rename(columns=column_mapping)

    # Eksik sütunları oluştur
    if 'title' not in df.columns:
        if 'content' in df.columns:
            df['title'] = df['content'].str[:100]
        else:
            raise ValueError("Veri kümesinde 'title' veya 'content' sütunu bulunamadı!")

    if 'content' not in df.columns:
        df['content'] = df['title']

    if 'category' not in df.columns:
        df['category'] = 'genel'

    return df[['title', 'content', 'category']]


def create_sample_data() -> pd.DataFrame:
    """İndirme başarısız olursa örnek veri oluştur."""
    data = {
        'title': [
            'Türkiye ekonomisi büyüme rakamları açıklandı',
            'Galatasaray Şampiyonlar Ligi maçında galip geldi',
            'Yapay zeka teknolojileri eğitimde devrim yaratıyor',
            'İstanbul hava durumu: Yağmur bekleniyor',
            'Sağlık Bakanlığı yeni aşı programını duyurdu',
            'Borsa İstanbul günü yükselişle kapattı',
            'Fenerbahçe transfer döneminde hareketli günler yaşıyor',
            'Elektrikli araç satışları rekor kırdı',
            'Deprem sonrası yeniden yapılanma çalışmaları sürüyor',
            'Üniversitelerde yapay zeka bölümleri açılıyor',
            'Merkez Bankası faiz kararını açıkladı',
            'Milli takım Avrupa Şampiyonası elemelerinde',
            'Siber güvenlik tehditleri artıyor',
            'Turizm sektörü rekor gelir elde etti',
            'Yeni eğitim öğretim yılı başladı',
            'Türk bilim insanları uzay araştırmalarında başarı elde etti',
            'Emekli maaşlarına zam yapıldı',
            'Basketbol Süper Ligi heyecanı devam ediyor',
            'Akıllı şehir projeleri hayata geçiriliyor',
            'Tarım sektöründe dijital dönüşüm hızlanıyor',
        ],
        'content': [
            'Türkiye İstatistik Kurumu, üçüncü çeyrek büyüme rakamlarını açıkladı. Gayri safi yurt içi hasıla bir önceki yılın aynı dönemine göre yüzde 3.8 büyüdü. Ekonomistler bu rakamın beklentilerin üzerinde olduğunu belirtti.',
            'Galatasaray, Şampiyonlar Ligi grup aşamasındaki kritik maçta rakibini 2-1 mağlup etti. Takımın gol kralı iki gol birden atarak galibiyetin mimarı oldu. Teknik direktör maç sonrası oyuncularını tebrik etti.',
            'Yapay zeka destekli eğitim platformları öğrencilerin bireysel öğrenme hızlarına uyum sağlıyor. Uzmanlar, kişiselleştirilmiş eğitimin akademik başarıyı artırdığını vurguluyor. Türkiye de bu alanda önemli adımlar atıyor.',
            'Meteoroloji Genel Müdürlüğü İstanbul için yağış uyarısında bulundu. Özellikle öğleden sonra başlaması beklenen yağmurun akşam saatlerinde etkisini artırması bekleniyor. Vatandaşlara dikkatli olmaları çağrısında bulunuldu.',
            'Sağlık Bakanlığı, yeni dönem aşılama programını kamuoyuyla paylaştı. Programda çocukluk çağı aşılarına ek olarak yetişkinlere yönelik hatırlatma dozları da yer alıyor. Aşılama kampanyası önümüzdeki ay başlayacak.',
            'Borsa İstanbul BIST 100 endeksi, günü yüzde 1.2 yükselişle kapattı. Bankacılık sektörü hisseleri öne çıkarken, teknoloji şirketleri de değer kazandı. Analistler yükseliş trendinin devam edebileceğini öngörüyor.',
            'Fenerbahçe, transfer döneminde birçok önemli oyuncuyla görüşmelerini sürdürüyor. Kulüp başkanı yaptığı açıklamada en az üç yeni transfer yapılacağını müjdeledi. Taraftarlar transferleri heyecanla bekliyor.',
            'Türkiye de elektrikli araç satışları geçen yıla göre yüzde 150 artış gösterdi. Yerli üretim modeller bu artışta önemli pay sahibi oldu. Şarj altyapısının genişletilmesi çalışmaları da hız kazandı.',
            'Deprem bölgesinde yeniden yapılanma çalışmaları tam hızla devam ediyor. Yeni depreme dayanıklı konutların inşaatı sürerken, altyapı projeleri de eş zamanlı yürütülüyor. Bölge halkı kalıcı konutlarına taşınmaya başladı.',
            'Türkiye genelinde birçok üniversite yapay zeka ve veri bilimi bölümleri açtı. YÖK verilerine göre bu alanlara olan talep son iki yılda üç kat arttı. Mezunların iş bulma oranının çok yüksek olduğu belirtiliyor.',
            'Türkiye Cumhuriyet Merkez Bankası, politika faiz oranını yüzde 45 seviyesinde sabit tutma kararı aldı. Karar piyasa beklentileriyle uyumlu bulundu. Enflasyonla mücadelenin kararlılıkla sürdürüleceği vurgulandı.',
            'A Milli Futbol Takımı, Avrupa Şampiyonası eleme grubundaki kritik maçta İzlanda ile karşılaştı. Mücadeleli geçen karşılaşmada milli takım sahadan 3-1 galip ayrıldı. Bu sonuçla grup liderliğini sürdürdü.',
            'Türkiye de siber saldırı vakaları son bir yılda yüzde 40 artış gösterdi. Uzmanlar özellikle fidye yazılımı saldırılarının kurumsal hedeflere yönelik arttığını belirtiyor. Siber güvenlik yatırımlarının artırılması gerektiği vurgulanıyor.',
            'Türkiye, turizm gelirlerinde yeni bir rekor kırdı. Kültür ve Turizm Bakanlığı verilerine göre yıllık turizm geliri 60 milyar doları aştı. En çok turist Almanya, Rusya ve İngiltere den geldi.',
            'Yeni eğitim öğretim yılı milyonlarca öğrencinin heyecanıyla başladı. Milli Eğitim Bakanlığı bu yıl müfredata yapay zeka ve kodlama derslerini ekledi. Okullar dijital altyapı açısından da güçlendirildi.',
            'Türk bilim insanları, uzay araştırmaları alanında önemli bir başarıya imza attı. Geliştirdikleri uydu sensörü teknolojisi uluslararası alanda büyük ilgi gördü. Proje NASA ile iş birliği kapsamında yürütülüyor.',
            'Emekli maaşlarına yapılan zam oranı belli oldu. SSK ve Bağ-Kur emeklilerinin maaşlarına yüzde 25 oranında artış uygulanacak. Yeni maaşlar önümüzdeki aydan itibaren ödenmeye başlanacak.',
            'Basketbol Süper Ligi nde heyecan doruk noktasına ulaştı. Lider Anadolu Efes, zorlu deplasmanı kazanarak zirvedeki yerini korudu. Playoff yarışı son haftalara doğru kızışıyor.',
            'İstanbul Büyükşehir Belediyesi akıllı şehir projelerini hayata geçirmeye devam ediyor. Akıllı trafik yönetim sistemi sayesinde trafik sıkışıklığı yüzde 15 azaldı. Projenin diğer illere de yaygınlaştırılması planlanıyor.',
            'Tarım sektöründe dijital dönüşüm hızla ilerliyor. Drone teknolojisi ve yapay zeka destekli tarım uygulamaları çiftçilerin verimliliğini artırıyor. Tarım ve Orman Bakanlığı dijital tarım desteklerini genişletiyor.',
        ],
        'category': [
            'ekonomi', 'spor', 'teknoloji', 'gündem', 'sağlık',
            'ekonomi', 'spor', 'teknoloji', 'gündem', 'eğitim',
            'ekonomi', 'spor', 'teknoloji', 'gündem', 'eğitim',
            'teknoloji', 'ekonomi', 'spor', 'teknoloji', 'teknoloji',
        ]
    }
    return pd.DataFrame(data)
