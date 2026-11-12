from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Lesson, Question, QuestionOption


GRAMMAR_LESSONS = [
    {
        "slug": "n5-particle-wa",
        "title": "Trợ từ は — nêu chủ đề câu",
        "objective": "Dùng は để nêu người/vật đang được nói đến; phân biệt chủ đề は với chủ ngữ mới が.",
        "content": {
            "summary": "は (đọc là wa) đánh dấu chủ đề: “nói về … thì …”. Từ đứng trước は thường đã được biết hoặc là chủ đề chung của cuộc hội thoại. は cũng có thể tạo sắc thái đối chiếu.",
            "usage": [
                "Mẫu cơ bản: Danh từ は thông tin. Ví dụ: わたしは学生です — Tôi là học sinh.",
                "は không đồng nghĩa hoàn toàn với “là”; nó đánh dấu chủ đề, còn です mới nối với danh từ/vị ngữ.",
                "Khi giới thiệu một sự vật mới hoặc muốn nhấn mạnh chủ thể thực hiện/trải nghiệm, thường dùng が; xem bài trợ từ が.",
            ],
            "examples": [
                {"japanese": "わたしは会社員です。", "reading": "わたしはかいしゃいんです。", "meaning": "Tôi là nhân viên công ty."},
                {"japanese": "今日は暑いです。", "reading": "きょうはあついです。", "meaning": "Hôm nay trời nóng."},
                {"japanese": "この店は日曜日は休みです。", "reading": "このみせはにちようびはやすみです。", "meaning": "Cửa hàng này nghỉ vào Chủ nhật."},
            ],
        },
        "questions": [
            ("わたし（　）学生です。", "Tôi là học sinh.", ["は", "が", "を", "で"], "は", "Câu giới thiệu thông tin về chủ đề わたし; dùng mẫu N は N です."),
            ("田中さん（　）日本人です。", "Anh/chị Tanaka là người Nhật.", ["は", "を", "に", "で"], "は", "Câu đang nêu thông tin về chủ đề 田中さん."),
            ("今日（　）水曜日です。", "Hôm nay là thứ Tư.", ["は", "が", "を", "と"], "は", "Hôm nay là chủ đề được nêu; dùng 今日 は."),
            ("このかばん（　）わたしのです。", "Cái cặp này là của tôi.", ["は", "を", "へ", "で"], "は", "Nêu cái cặp này làm chủ đề, sau đó nói nó thuộc về ai."),
        ],
    },
    {
        "slug": "n5-particle-ga",
        "title": "Trợ từ が — chủ thể và điều được nhận biết",
        "objective": "Dùng が để đánh dấu chủ thể mới, người/vật tồn tại, hoặc điều thích và có thể làm.",
        "content": {
            "summary": "が thường đánh dấu chủ thể trực tiếp của hành động/trạng thái. N5 hay gặp が trong câu tồn tại います／あります và với 好き・きらい・上手・わかります.",
            "usage": [
                "Có người/con vật/sự vật: N が います／あります. Ví dụ: ねこがいます — Có một con mèo.",
                "Điều thích/hiểu/giỏi: N が 好きです／わかります／上手です.",
                "は giới thiệu chủ đề hoặc đối chiếu; が tập trung vào chủ thể hoặc thông tin mới: 部屋には猫がいます — Trong phòng có mèo.",
            ],
            "examples": [
                {"japanese": "公園に子どもがいます。", "reading": "こうえんにこどもがいます。", "meaning": "Có trẻ em ở công viên."},
                {"japanese": "わたしは音楽が好きです。", "reading": "わたしはおんがくがすきです。", "meaning": "Tôi thích âm nhạc."},
                {"japanese": "駅の前に銀行があります。", "reading": "えきのまえにぎんこうがあります。", "meaning": "Có ngân hàng ở trước ga."},
            ],
        },
        "questions": [
            ("教室に学生（　）います。", "Có học sinh trong lớp.", ["が", "は", "を", "で"], "が", "います diễn tả sự tồn tại; người/vật tồn tại được đánh dấu bằng が."),
            ("わたしはコーヒー（　）好きです。", "Tôi thích cà phê.", ["が", "を", "に", "へ"], "が", "好きです đi với điều được yêu thích + が."),
            ("どこ（　）富士山が見えますか。", "Có thể nhìn thấy núi Phú Sĩ ở đâu?", ["で", "に", "を", "と"], "で", "で đánh dấu địa điểm nơi diễn ra việc nhìn thấy núi Phú Sĩ."),
            ("日本語（　）わかります。", "Tôi hiểu tiếng Nhật.", ["が", "を", "へ", "も"], "が", "わかります thường đi với nội dung được hiểu + が."),
        ],
    },
    {
        "slug": "n5-particle-wo",
        "title": "Trợ từ を — tân ngữ trực tiếp",
        "objective": "Đánh dấu đối tượng trực tiếp của hành động; dùng với các động từ như ăn, uống, đọc, xem.",
        "content": {
            "summary": "を (đọc là o) đứng sau đối tượng trực tiếp chịu tác động của động từ. Không nhầm với が trong các mẫu 好きです và わかります.",
            "usage": [
                "Mẫu: người は vật を động từ. を đứng ngay sau thứ được ăn, đọc, xem hoặc mua.",
                "Một số động từ chuyển động dùng を cho nơi đi qua/rời khỏi: 公園を散歩します — đi dạo qua công viên.",
                "を thường không dùng với động từ tồn tại います／あります.",
            ],
            "examples": [
                {"japanese": "毎朝パンを食べます。", "reading": "まいあさパンをたべます。", "meaning": "Mỗi sáng tôi ăn bánh mì."},
                {"japanese": "図書館で本を読みます。", "reading": "としょかんでほんをよみます。", "meaning": "Tôi đọc sách ở thư viện."},
                {"japanese": "日曜日に映画を見ました。", "reading": "にちようびにえいがをみました。", "meaning": "Tôi đã xem phim vào Chủ nhật."},
            ],
        },
        "questions": [
            ("朝ごはんに卵（　）食べます。", "Tôi ăn trứng vào bữa sáng.", ["を", "が", "に", "で"], "を", "卵 là đối tượng trực tiếp của động từ 食べます."),
            ("駅で新聞（　）買いました。", "Tôi đã mua báo ở ga.", ["を", "へ", "が", "と"], "を", "新聞 là thứ được mua; đánh dấu tân ngữ bằng を."),
            ("夜、テレビ（　）見ます。", "Buổi tối tôi xem tivi.", ["を", "に", "から", "も"], "を", "テレビ là đối tượng của động từ 見ます."),
            ("公園（　）散歩します。", "Tôi đi dạo trong/qua công viên.", ["を", "が", "の", "と"], "を", "を có thể đánh dấu nơi đi qua với động từ chuyển động như 散歩します."),
        ],
    },
    {
        "slug": "n5-particle-ni",
        "title": "Trợ từ に — thời điểm, đích đến và vị trí tồn tại",
        "objective": "Nhận biết に khi chỉ thời điểm cụ thể, nơi đến/điểm đến hoặc vị trí có người/vật tồn tại.",
        "content": {
            "summary": "に đánh dấu một điểm cụ thể: thời điểm, đích đến/đối tượng nhận, hoặc vị trí nơi người/vật hiện diện. Chọn nghĩa dựa trên động từ và ngữ cảnh.",
            "usage": [
                "Thời điểm cụ thể: 7時に起きます — thức dậy lúc 7 giờ. Thường không thêm に sau 今日, 明日, 毎日.",
                "Đích đến/đối tượng nhận: 学校に行きます／友だちに電話します.",
                "Vị trí tồn tại với います／あります: 机の上に本があります.",
            ],
            "examples": [
                {"japanese": "毎朝六時に起きます。", "reading": "まいあさろくじにおきます。", "meaning": "Mỗi sáng tôi thức dậy lúc sáu giờ."},
                {"japanese": "来週、京都に行きます。", "reading": "らいしゅう、きょうとにいきます。", "meaning": "Tuần sau tôi đi Kyoto."},
                {"japanese": "母は台所にいます。", "reading": "はははだいどころにいます。", "meaning": "Mẹ đang ở trong bếp."},
            ],
        },
        "questions": [
            ("毎晩十一時（　）寝ます。", "Tối nào tôi cũng ngủ lúc 11 giờ.", ["に", "で", "を", "と"], "に", "Giờ cụ thể 十一時 được đánh dấu bằng に."),
            ("来月、日本（　）行きます。", "Tháng sau tôi đi Nhật.", ["に", "を", "が", "で"], "に", "に đánh dấu đích đến của 行きます."),
            ("机の上（　）辞書があります。", "Có cuốn từ điển trên bàn.", ["に", "を", "へ", "と"], "に", "Vị trí tồn tại với あります dùng に."),
            ("友だち（　）手紙を書きます。", "Tôi viết thư cho bạn.", ["に", "で", "を", "から"], "に", "Người nhận/đối tượng hướng đến của 書きます được đánh dấu bằng に."),
        ],
    },
    {
        "slug": "n5-particle-de",
        "title": "Trợ từ で — nơi diễn ra hành động và phương tiện",
        "objective": "Dùng で để chỉ địa điểm có hành động xảy ra, phương tiện hoặc cách thức thực hiện.",
        "content": {
            "summary": "で thường đánh dấu nơi một hành động diễn ra hoặc công cụ/phương tiện dùng để làm việc đó. So sánh: 公園で遊ぶ (hành động ở công viên) và 公園にいる (có mặt tại công viên).",
            "usage": [
                "Địa điểm hành động: 図書館で勉強します — học ở thư viện.",
                "Phương tiện/công cụ: バスで行きます／箸で食べます.",
                "Quốc gia/ngôn ngữ hoặc nhóm thực hiện: 日本語で話します／三人で行きます.",
            ],
            "examples": [
                {"japanese": "カフェで友だちと話しました。", "reading": "カフェでともだちとはなしました。", "meaning": "Tôi đã trò chuyện với bạn ở quán cà phê."},
                {"japanese": "バスで会社へ行きます。", "reading": "バスでかいしゃへいきます。", "meaning": "Tôi đi làm bằng xe buýt."},
                {"japanese": "はしで魚を食べます。", "reading": "はしでさかなをたべます。", "meaning": "Tôi ăn cá bằng đũa."},
            ],
        },
        "questions": [
            ("図書館（　）日本語を勉強します。", "Tôi học tiếng Nhật ở thư viện.", ["で", "に", "を", "へ"], "で", "勉強する là hành động diễn ra tại thư viện; dùng で."),
            ("毎日、自転車（　）学校へ行きます。", "Mỗi ngày tôi đi học bằng xe đạp.", ["で", "に", "が", "と"], "で", "で đánh dấu phương tiện di chuyển."),
            ("はし（　）ごはんを食べます。", "Tôi ăn cơm bằng đũa.", ["で", "を", "へ", "の"], "で", "で chỉ công cụ dùng để ăn."),
            ("日本語（　）名前を書いてください。", "Xin hãy viết tên bằng tiếng Nhật.", ["で", "に", "が", "から"], "で", "で chỉ ngôn ngữ/cách thức thực hiện."),
        ],
    },
    {
        "slug": "n5-particle-e",
        "title": "Trợ từ へ — hướng di chuyển",
        "objective": "Dùng へ (đọc là e) để nêu hướng/đích di chuyển; phân biệt sắc thái với に.",
        "content": {
            "summary": "へ (đọc là e, không phải he) đứng sau địa điểm để chỉ hướng đi. Mẫu thường gặp: địa điểm へ 行きます／来ます／帰ります. に cũng có thể dùng với các động từ này và nhấn mạnh điểm đến.",
            "usage": [
                "へ nhấn mạnh hướng di chuyển; に nhấn mạnh nơi đến. Trong các câu đi/đến/về cơ bản, cả hai thường dùng được.",
                "Chỉ dùng へ trong ngữ cảnh có chuyển động như 行く, 来る, 帰る; không dùng để nói vị trí đang ở.",
                "へ được phát âm là e khi làm trợ từ.",
            ],
            "examples": [
                {"japanese": "これから駅へ行きます。", "reading": "これからえきへいきます。", "meaning": "Bây giờ tôi đi về phía nhà ga."},
                {"japanese": "夏休みに国へ帰ります。", "reading": "なつやすみにくにへかえります。", "meaning": "Kỳ nghỉ hè tôi về quê/nước."},
                {"japanese": "友だちが家へ来ます。", "reading": "ともだちがいえへきます。", "meaning": "Bạn tôi sẽ đến nhà."},
            ],
        },
        "questions": [
            ("来週、大阪（　）行きます。", "Tuần sau tôi đi Osaka.", ["へ", "を", "で", "の"], "へ", "へ chỉ hướng/đích di chuyển với 行きます."),
            ("仕事のあと、家（　）帰ります。", "Sau giờ làm, tôi về nhà.", ["へ", "が", "を", "で"], "へ", "へ có thể dùng với 帰ります để chỉ hướng về nhà."),
            ("友だちは日本（　）来ました。", "Bạn tôi đã đến Nhật.", ["へ", "を", "と", "で"], "へ", "へ đánh dấu hướng đến với 来ました."),
            ("日曜日、海（　）行きませんか。", "Chủ nhật, bạn có đi biển không?", ["へ", "が", "を", "の"], "へ", "Địa điểm đứng trước へ là hướng đến của 行きませんか."),
        ],
    },
    {
        "slug": "n5-particle-no",
        "title": "Trợ từ の — sở hữu và bổ nghĩa danh từ",
        "objective": "Nối hai danh từ để chỉ sở hữu, quan hệ hoặc phân loại/mô tả.",
        "content": {
            "summary": "の nối hai danh từ. Danh từ trước の bổ nghĩa cho danh từ sau: có thể chỉ sở hữu, mối quan hệ, nơi chốn hoặc loại/đặc điểm.",
            "usage": [
                "Sở hữu: わたしの本 — sách của tôi.",
                "Quan hệ/cơ quan: 友だちの妹 — em gái của bạn; 日本語の先生 — giáo viên tiếng Nhật.",
                "Danh từ sau の có thể được lược nếu đã rõ: これはだれのですか — Cái này là của ai?",
            ],
            "examples": [
                {"japanese": "これは父の車です。", "reading": "これはちちのくるまです。", "meaning": "Đây là xe của bố tôi."},
                {"japanese": "大学の友だちと昼ごはんを食べます。", "reading": "だいがくのともだちとひるごはんをたべます。", "meaning": "Tôi ăn trưa với bạn ở trường đại học."},
                {"japanese": "日本語の本を買いました。", "reading": "にほんごのほんをかいました。", "meaning": "Tôi đã mua sách tiếng Nhật."},
            ],
        },
        "questions": [
            ("これはわたし（　）傘です。", "Đây là ô của tôi.", ["の", "に", "を", "へ"], "の", "の nối người sở hữu わたし với danh từ 傘."),
            ("あの人は日本語（　）先生です。", "Người kia là giáo viên tiếng Nhật.", ["の", "で", "が", "を"], "の", "Danh từ 日本語 bổ nghĩa cho 先生 qua の."),
            ("これはだれ（　）かばんですか。", "Đây là cặp của ai?", ["の", "へ", "で", "を"], "の", "Mẫu hỏi sở hữu là だれのかばん."),
            ("駅（　）前で会いましょう。", "Hãy gặp nhau trước nhà ga.", ["の", "に", "が", "と"], "の", "駅の前 là cấu trúc danh từ + の + vị trí 前."),
        ],
    },
    {
        "slug": "n5-particle-to",
        "title": "Trợ từ と — cùng với và liệt kê đầy đủ",
        "objective": "Dùng と cho người đồng hành hoặc nối các danh từ trong danh sách đầy đủ.",
        "content": {
            "summary": "と dùng để liệt kê các danh từ trong một danh sách đầy đủ hoặc chỉ người cùng thực hiện hành động. Trong nghĩa “và”, と thường hàm ý nêu những món cụ thể trong danh sách.",
            "usage": [
                "Người đồng hành: 友だちと映画を見ます — xem phim cùng bạn.",
                "Liệt kê đầy đủ: パンと牛乳を買います — mua bánh mì và sữa (các món được nêu).",
                "Không nhầm と (cùng với) với で (địa điểm/phương tiện).",
            ],
            "examples": [
                {"japanese": "妹と買い物に行きました。", "reading": "いもうととかいものにいきました。", "meaning": "Tôi đã đi mua sắm cùng em gái."},
                {"japanese": "りんごとバナナをください。", "reading": "りんごとバナナをください。", "meaning": "Cho tôi táo và chuối."},
                {"japanese": "週末、家族と公園へ行きます。", "reading": "しゅうまつ、かぞくとこうえんへいきます。", "meaning": "Cuối tuần tôi đi công viên cùng gia đình."},
            ],
        },
        "questions": [
            ("土曜日、友だち（　）テニスをします。", "Thứ Bảy tôi chơi tennis với bạn.", ["と", "で", "に", "を"], "と", "Người cùng thực hiện hành động đi với と."),
            ("スーパーで牛乳（　）卵を買いました。", "Tôi đã mua sữa và trứng ở siêu thị.", ["と", "が", "へ", "に"], "と", "と nối các danh từ được liệt kê."),
            ("兄（　）晩ごはんを作ります。", "Tôi nấu bữa tối cùng anh trai.", ["と", "で", "を", "の"], "と", "兄 là người cùng nấu; dùng と."),
            ("ノート（　）鉛筆を持ってきてください。", "Hãy mang vở và bút chì đến.", ["と", "に", "が", "へ"], "と", "Liệt kê hai vật bằng と."),
        ],
    },
    {
        "slug": "n5-particle-mo",
        "title": "Trợ từ も — cũng, cũng không",
        "objective": "Dùng も thay cho は／が／を để thể hiện thông tin tương tự hoặc phủ định tương ứng.",
        "content": {
            "summary": "も mang nghĩa “cũng”, thay cho trợ từ chủ đề hoặc tân ngữ khi thông tin được thêm vào cùng nhóm. Trong câu phủ định, も có thể mang nghĩa “cũng không”.",
            "usage": [
                "Thêm chủ thể: わたしも学生です — Tôi cũng là học sinh.",
                "Thêm tân ngữ: コーヒーも飲みます — Tôi cũng uống cà phê (ngoài món đã nhắc).",
                "Phủ định: 何も食べません — Tôi không ăn gì cả; だれもいません — Không có ai.",
            ],
            "examples": [
                {"japanese": "姉は大学生です。兄も大学生です。", "reading": "あねはだいがくせいです。あにもだいがくせいです。", "meaning": "Chị tôi là sinh viên đại học. Anh tôi cũng là sinh viên."},
                {"japanese": "日曜日も働きます。", "reading": "にちようびもはたらきます。", "meaning": "Chủ nhật tôi cũng làm việc."},
                {"japanese": "今日は何も買いませんでした。", "reading": "きょうはなにもかいませんでした。", "meaning": "Hôm nay tôi không mua gì cả."},
            ],
        },
        "questions": [
            ("田中さんは先生です。山田さん（　）先生です。", "Anh/chị Tanaka là giáo viên. Anh/chị Yamada cũng là giáo viên.", ["も", "を", "で", "へ"], "も", "Cùng thông tin với câu trước nên dùng も với nghĩa “cũng”."),
            ("わたしは水を飲みます。お茶（　）飲みます。", "Tôi uống nước. Tôi cũng uống trà.", ["も", "が", "に", "と"], "も", "も thêm trà vào nhóm đồ uống, thay cho を."),
            ("日曜日（　）会社へ行きます。", "Chủ nhật tôi cũng đi công ty.", ["も", "を", "で", "が"], "も", "も nhấn mạnh ngày Chủ nhật cũng giống các ngày khác."),
            ("冷蔵庫に何（　）ありません。", "Trong tủ lạnh không có gì cả.", ["も", "が", "を", "へ"], "も", "何も kết hợp với vị ngữ phủ định để nói “không ... gì cả”."),
        ],
    },
    {
        "slug": "n5-particles-kara-made",
        "title": "Trợ từ から・まで — từ … đến …",
        "objective": "Nêu điểm bắt đầu và điểm kết thúc của thời gian hoặc phạm vi.",
        "content": {
            "summary": "から đánh dấu điểm bắt đầu (“từ”), còn まで đánh dấu điểm kết thúc/giới hạn (“đến”). Có thể dùng riêng từng trợ từ hoặc ghép から～まで.",
            "usage": [
                "Thời gian: 9時から5時まで働きます — làm từ 9 giờ đến 5 giờ.",
                "Khoảng cách/điểm: 東京から大阪まで — từ Tokyo đến Osaka.",
                "Danh từ chỉ thời gian bắt đầu/kết thúc đứng ngay trước から／まで.",
            ],
            "examples": [
                {"japanese": "銀行は九時から三時までです。", "reading": "ぎんこうはくじからさんじまでです。", "meaning": "Ngân hàng mở từ 9 giờ đến 3 giờ."},
                {"japanese": "家から駅まで歩きます。", "reading": "いえからえきまであるきます。", "meaning": "Tôi đi bộ từ nhà đến ga."},
                {"japanese": "月曜日から金曜日まで学校があります。", "reading": "げつようびからきんようびまでがっこうがあります。", "meaning": "Từ thứ Hai đến thứ Sáu có học ở trường."},
            ],
        },
        "questions": [
            ("授業は九時（　）始まります。", "Buổi học bắt đầu từ 9 giờ.", ["から", "まで", "に", "で"], "から", "から đánh dấu thời điểm bắt đầu."),
            ("デパートは夜八時（　）開いています。", "Cửa hàng bách hóa mở đến 8 giờ tối.", ["まで", "から", "を", "へ"], "まで", "まで đánh dấu giới hạn/thời điểm kết thúc."),
            ("毎日、八時（　）五時まで働きます。", "Mỗi ngày tôi làm từ 8 giờ đến 5 giờ.", ["から", "まで", "で", "に"], "から", "Cặp khoảng thời gian có dạng điểm bắt đầu から, kết thúc まで."),
            ("この電車は東京（　）京都まで行きます。", "Tàu này đi từ Tokyo đến Kyoto.", ["から", "まで", "を", "の"], "から", "東京 là điểm khởi hành, được đánh dấu bằng から."),
        ],
    },
    {
        "slug": "n5-particle-ka",
        "title": "Trợ từ か — câu hỏi và lựa chọn",
        "objective": "Tạo câu hỏi lịch sự với か và nêu lựa chọn A hay B.",
        "content": {
            "summary": "か đứng cuối câu để tạo câu hỏi lịch sự. Trong hội thoại thân mật có thể bỏ か và lên giọng, nhưng người mới học nên dùng đúng mẫu lịch sự. A か B か nêu các lựa chọn.",
            "usage": [
                "Câu hỏi lịch sự: これは何ですか — Đây là cái gì?",
                "Hỏi có/không: コーヒーを飲みますか — Bạn có uống cà phê không?",
                "Lựa chọn: 電車かバスで行きます — đi bằng tàu điện hay xe buýt.",
            ],
            "examples": [
                {"japanese": "明日、学校へ行きますか。", "reading": "あした、がっこうへいきますか。", "meaning": "Ngày mai bạn có đi học không?"},
                {"japanese": "これはだれの本ですか。", "reading": "これはだれのほんですか。", "meaning": "Đây là sách của ai?"},
                {"japanese": "昼ごはんはうどんかそばを食べます。", "reading": "ひるごはんはうどんかそばをたべます。", "meaning": "Bữa trưa tôi ăn udon hoặc soba."},
            ],
        },
        "questions": [
            ("お名前は何です（　）。", "Tên bạn là gì?", ["か", "を", "に", "で"], "か", "か đặt cuối câu để tạo câu hỏi lịch sự."),
            ("コーヒーを飲みます（　）。", "Bạn có uống cà phê không?", ["か", "が", "の", "へ"], "か", "Câu hỏi có/không lịch sự kết thúc bằng か."),
            ("駅までバス（　）電車で行きます。", "Tôi đi đến ga bằng xe buýt hoặc tàu điện.", ["か", "も", "を", "に"], "か", "か nối các lựa chọn: xe buýt hoặc tàu điện."),
            ("トイレはどこです（　）。", "Nhà vệ sinh ở đâu?", ["か", "と", "で", "が"], "か", "どこですか là mẫu hỏi địa điểm lịch sự."),
        ],
    },
]


def validate_curriculum() -> None:
    slugs: set[str] = set()
    for lesson in GRAMMAR_LESSONS:
        if lesson["slug"] in slugs:
            raise ValueError(f"Duplicate grammar lesson slug: {lesson['slug']}")
        slugs.add(lesson["slug"])
        if not lesson["content"]["summary"] or len(lesson["content"]["examples"]) < 2:
            raise ValueError(f"Incomplete grammar lesson content: {lesson['slug']}")
        if len(lesson["questions"]) < 4:
            raise ValueError(f"Grammar lesson needs at least four exercises: {lesson['slug']}")
        for sentence, translation, options, correct, explanation in lesson["questions"]:
            if not sentence or not translation or correct not in options or len(set(options)) != len(options):
                raise ValueError(f"Invalid exercise in grammar lesson: {lesson['slug']}")
            if not explanation:
                raise ValueError(f"Missing exercise explanation in grammar lesson: {lesson['slug']}")


def seed_grammar_n5(db: Session) -> int:
    validate_curriculum()
    category = db.scalar(select(Category).where(Category.slug == "grammar-n5"))
    if category is None:
        category = Category(slug="grammar-n5", name="Ngữ pháp N5")
        db.add(category)
        db.flush()
    else:
        category.name = "Ngữ pháp N5"

    for position, lesson_data in enumerate(GRAMMAR_LESSONS, start=1):
        lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_data["slug"]))
        if lesson is None:
            lesson = Lesson(
                category_id=category.id,
                slug=lesson_data["slug"],
                title=lesson_data["title"],
                lesson_type="grammar",
                level="N5",
                position=position,
            )
            db.add(lesson)
            db.flush()

        lesson.category_id = category.id
        lesson.title = lesson_data["title"]
        lesson.lesson_type = "grammar"
        lesson.level = "N5"
        lesson.objective = lesson_data["objective"]
        lesson.content = lesson_data["content"]
        lesson.status = "published"
        lesson.version = 1
        lesson.position = position
        db.flush()

        existing_questions = {
            question.position: question
            for question in db.scalars(
                select(Question).where(Question.lesson_id == lesson.id)
            )
        }
        for question_position, (sentence, translation, options, correct, explanation) in enumerate(
            lesson_data["questions"], start=1
        ):
            question = existing_questions.pop(question_position, None)
            if question is None:
                question = Question(
                    lesson_id=lesson.id,
                    question_type="multiple_choice",
                    prompt={},
                    position=question_position,
                )
                db.add(question)
                db.flush()
            question.question_type = "multiple_choice"
            question.prompt = {"sentence": sentence, "translation": translation}
            question.explanation = explanation
            question.position = question_position
            question.difficulty = 1
            question.is_active = True
            db.flush()

            existing_options = {
                option.text: option
                for option in db.scalars(
                    select(QuestionOption).where(QuestionOption.question_id == question.id)
                )
            }
            for option_text in options:
                option = existing_options.pop(option_text, None)
                if option is None:
                    option = QuestionOption(question_id=question.id, text=option_text)
                    db.add(option)
                option.is_correct = option_text == correct
                option.explanation = explanation
            for stale_option in existing_options.values():
                db.delete(stale_option)

        for stale_question in existing_questions.values():
            db.delete(stale_question)

    db.flush()
    return len(GRAMMAR_LESSONS)


if __name__ == "__main__":
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        count = seed_grammar_n5(db)
        db.commit()
    print(f"Published {count} N5 grammar lessons")
