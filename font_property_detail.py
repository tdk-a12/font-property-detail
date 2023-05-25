import os
import fontTools.ttLib
from enum import IntEnum, unique
from logging import getLogger
import coloredlogs

# ログ出力の設定
logger = getLogger("Font Property Detail")
coloredlogs.install(level="INFO")

class Font():
    """フォント"""

    @unique
    class Platform(IntEnum):
        """
        プラットフォームID\n
        https://learn.microsoft.com/en-us/typography/opentype/spec/name#platform-ids
        """
        ALL = -1
        MAC = 1
        WINDOWS = 3

        @classmethod
        def get_name_by_id(cls, id):
            """IDからクラス内の定数名取得"""
            for member in cls:
                # クラス内の定数の値とIDが一致
                if member == id:
                    return member.name
            
            return "Unknown"
            
    @unique
    class Name(IntEnum):
        """
        ネームID\n
        プロパティ詳細で確認できる情報\n
        https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
        """
        COPY_RIGHT = 0
        """著作権"""
        FONT_FAMILY_NAME = 1
        """フォントのファミリー名"""
        FONT_SUBFAMILY_NAME = 2
        """フォントのサブファミリー名(フォントのスタイル)"""
        UNIQUE_FONT_IDENTIFIER = 3
        """一意のフォント識別子"""
        FULL_FONT_NAME = 4
        """完全なフォント名"""
        VERSION_STRING = 5
        """ファイルバージョン"""
        POSTSCRIPT_NAME = 6
        """フォントのPostScript名"""
        TRADEMARK = 7
        """商標"""
        MANUFACTURER_NAME = 8
        """製造者"""
        DESIGNER = 9
        """デザイナーの名前"""
        DESCRIPTION = 10
        """ファイルの説明"""
        URL_VENDOR = 11
        """ベンダーのURL"""
        URL_DESIGNER = 12
        """デザイナーのURL"""
        LICENSE_DESCRIPTION = 13
        """ライセンスの説明"""
        LICENSE_INFO_URL = 14
        """ライセンス情報のURL"""
        TYPOGRAPHIC_FAMILY_NAME = 16
        """印刷用のファミリー名"""
        TYPOGRAPHIC_SUBFAMILY_NAME = 17
        """印刷用のサブファミリー名"""
        COMPATIBLE_FULL = 18
        """互換性のあるフルネーム (Macのみ)"""
        SAMPLE_TEXT = 19
        """サンプルテキスト"""
        POSTSCRIPT_CID_FINDFONT_NAME = 20
        """PostScript CID findfont名"""
        WWS_FAMILY_NAME = 21
        """WWSファミリー名"""
        WWS_SUBFAMILY_NAME = 22
        """WWSサブファミリー名"""
        LIGHT_BACKGROUND_PALETTE = 23
        """明るい背景パレット (CPALテーブル)"""
        DARK_BACKGROUND_PALETTE = 24
        """暗い背景パレット (CPALテーブル)"""
        VARIATIONS_POSTSCRIPT_NAME_PREFIX = 25
        """バリエーションのPostScript名の接頭語"""
        
        @classmethod
        def get_name_by_id(cls, id):
            """IDからクラス内の定数名取得"""
            for member in cls:
                # クラス内の定数の値とIDが一致
                if member == id:
                    return member.name
            
            return "Unknown"

    @unique
    class WindowsLanguage(IntEnum):
        """
        Windows言語ID\n
        https://learn.microsoft.com/en-us/typography/opentype/spec/name#windows-language-ids
        """
        ALL = -1
        ENGLISH_UNITED_STATES = 1033
        JAPANESE = 1041

        @classmethod
        def get_name_by_id(cls, id):
            """IDからクラス内の定数名取得"""
            for member in cls:
                # クラス内の定数の値とIDが一致
                if member == id:
                    return member.name
            
            return "Unknown"

    @unique
    class MacLanguage(IntEnum):
        """
        Mac言語ID\n
        https://learn.microsoft.com/en-us/typography/opentype/spec/name#macintosh-language-ids
        """
        ALL = -1
        ENGLISH = 0
        JAPANESE = 11

        @classmethod
        def get_name_by_id(cls, id):
            """IDからクラス内の定数名取得"""
            for member in cls:
                # クラス内の定数の値とIDが一致
                if member == id:
                    return member.name
            
            return "Unknown"

    font_file_path = ""
    """フォントのファイルパス"""

    def __init__(self, file_path) -> None:
        self.font_file_path = file_path

    def get_property_detail(self, name_id, platform_id=Platform.ALL, lang_id=WindowsLanguage.ALL):
        """フォントのプロパティ詳細取得"""
        # 拡張子取得
        file_extension = os.path.splitext(self.font_file_path)[1].lower()
        
        property_dict = {}
        try:
            # TTCフォントファイル
            if file_extension == ".ttc":
                font_collection = fontTools.ttLib.TTCollection(self.font_file_path)
                for font_number, font in enumerate(font_collection):
                    self.process_property_detail(font, name_id, platform_id, lang_id, property_dict)

            # TTFまたはOTFフォントファイル
            elif file_extension == ".ttf" or file_extension == ".otf":
                font = fontTools.ttLib.TTFont(self.font_file_path)
                self.process_property_detail(font, name_id, platform_id, lang_id, property_dict)

            # 上記以外
            else:
                logger.warning("サポートされていないフォントファイル形式です")

        except fontTools.ttLib.TTLibFileIsCollectionError as e:
            logger.error(f"フォントファイルのコレクションの読み込みエラー: {e}")

        except fontTools.ttLib.TTLibError as e:
            logger.error(f"フォントファイルの読み込みエラー: {e}")

        except FileNotFoundError as e:
            logger.error(f"フォントファイルが見つかりませんでした: {e}")

        return property_dict

    def process_property_detail(self, font, name_id, platform_id, lang_id, property_dict):
        """フォントのプロパティ詳細取得の処理"""
        # プロパティ詳細取得
        property_dict = self.get_value_for_name_table(font, name_id, platform_id=platform_id, lang_id=lang_id)
        # プロパティ詳細ログ出力
        self.logging_property_detail(property_dict)

    def logging_property_detail(self, property_dict):
        """フォントのプロパティ詳細ログ出力"""
        for property in property_dict:
            name = property["name"]
            platform = property["platform"]
            lang = property["lang"]
            value = property["value"]
            logger.info(f"{name} ({platform}, {lang}): {value}")

    def get_value_for_name_table(self, font, name_id, platform_id=Platform.ALL, lang_id=WindowsLanguage.ALL):
        """フォントのネームテーブル内から値取得"""
        logger.debug(f"引数: font: {font}, name_id: {name_id}, platform_id: {platform_id}, lang_id: {lang_id}")
        # フォントファイルからネームテーブル取得
        name_table = font['name']

        # 値リスト
        value_list = []

        # ネームテーブル内のレコードを走査
        for record in name_table.names:
            logger.debug(f"PlatformID: {record.platformID}, LangID: {record.langID}, NameID: {record.nameID}, record: {record}")

            # レコードのネームIDと指定したネームIDが一致
            if record.nameID == name_id.value:
                # 値リストにレコードのフォーマット済みディクショナリを追加
                value_list.append(self.get_formatted_dict(record))

            # レコードが条件に一致
            if self.is_matching_record(record, name_id, platform_id, lang_id):
                # 走査終了
                break
        
        # 値リストなし
        if not value_list:
            logger.warning(f"プロパティ '{name_id.name}' が見つかりませんでした")

        return value_list

    def is_matching_record(self, record, name_id, platform_id, lang_id):
        """レコードの一致可否"""
        # レコードのプラットフォームID、言語ID、ネームIDと指定した同IDが一致する場合はTrue
        return (
            record.platformID == platform_id.value
            and record.langID == lang_id.value
            and record.nameID == name_id.value
        )

    def get_formatted_dict(self, record):
        """レコードのフォーマット済みディクショナリ取得"""
        # インスタンス生成
        platform = Font.Platform(record.platformID)
        name = Font.Name(record.nameID) 
        lang = None

        # プラットフォームIDがWindows
        if record.platformID == Font.Platform.WINDOWS:
            # Windows言語IDのインスタンス生成
            lang = Font.WindowsLanguage(record.langID)
        # プラットフォームIDがMac
        elif record.platformID == Font.Platform.MAC:
            # Mac言語IDのインスタンス生成
            lang = Font.MacLanguage(record.langID)
        # 上記以外
        else:
            logger.warning(f"サポートされていないプラットフォームが含まれています。platformID: {record.platformID}")

        # 言語IDのインスタンスあり
        if lang is not None:
            return {
                "name": name.get_name_by_id(record.nameID),
                "platform": platform.get_name_by_id(record.platformID),
                "lang": lang.get_name_by_id(record.langID),
                "value": str(record)
            }
        # 上記以外
        else:
            return {
                "name": name.get_name_by_id(record.nameID),
                "platform": platform.get_name_by_id(record.platformID),
                "lang": "Unknown",
                "value": str(record)
            }

    def get_font_family_name(self):
        """フォントのファミリー名取得"""
        # フォントのプロパティ詳細取得
        return self.get_property_detail(font.Name.FONT_FAMILY_NAME)

    def get_license_description(self):
        """ライセンスの説明取得"""
        # フォントのプロパティ詳細取得
        return self.get_property_detail(font.Name.LICENSE_DESCRIPTION)

if __name__ == "__main__":
    # フォントファイルのパスを指定してプロパティ詳細を取得する
    font_file_path = "Bowli_rough_font-Regular.ttf"

    font = Font(font_file_path)

    font.get_font_family_name()
    font.get_license_description()
