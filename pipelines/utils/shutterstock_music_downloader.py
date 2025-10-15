import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class ShutterstockMusicDownloader:
    def __init__(self, download_dir="./shutterstock_music", browser="chrome"):
        self.download_dir = os.path.abspath(download_dir)
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        self.download_dir = os.path.abspath(download_dir)
        self.browser = browser.lower()
        self.driver = None
        self.wait = None
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"创建下载目录: {self.download_dir}")

    # Has to open browser with debug mode first    
    def connect_to_existing_browser(self, debug_port=9222):
        if self.browser == "chrome":
            chrome_options = ChromeOptions()
            
            try:
                chrome_options.add_experimental_option("debuggerAddress", f"localhost:{debug_port}")
                self.driver = webdriver.Chrome(options=chrome_options)
                print(f"成功连接到现有的{self.browser.title()}浏览器会话")
            except Exception as e:
                print(f"无法连接到现有会话: {e}")
                print("正在启动新的Chrome调试会话...")
                
                # 如果连接失败，启动新的Chrome实例 -- Most time suffer to this
                chrome_options = ChromeOptions()
                chrome_options.add_argument(f"--remote-debugging-port={debug_port}")
                chrome_options.add_argument("--user-data-dir=/tmp/chrome_debug")
                
                self.driver = webdriver.Chrome(options=chrome_options)
                print("已启动新的Chrome调试会话")
                print("请在浏览器中打开Shutterstock页面")
                
        else:
            print("Safari不支持连接到现有会话，请使用Chrome浏览器")
            return False
            
        self.wait = WebDriverWait(self.driver, 10)
        return True
    
    def wait_for_element(self, by, value, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    
    def humanized_delay(self, min_seconds, max_seconds):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def humanize_delay(self, min_seconds, max_seconds):
        return self.humanized_delay(min_seconds, max_seconds)

    def safe_click_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        self.humanized_delay(0.2, 0.6)
        
        wait = WebDriverWait(self.driver, 10)
        clickable_element = wait.until(EC.element_to_be_clickable(element))
        
        clickable_element.click()
        return True

    def download_single_track(self, track_element, track_index):
        print(f"\n开始下载第 {track_index} 首音乐...")
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", track_element)
        self.humanized_delay(1, 2)
        
        # 1. 查找并点击Try按钮
        try:
            try_button = track_element.find_element(By.CSS_SELECTOR, "button[aria-label='Try']")
            
            if try_button and try_button.is_displayed() and try_button.is_enabled():
                
                if self.safe_click_element(try_button):
                    self.humanized_delay(1, 2)
                else:
                    print("点击Try按钮失败")
                    return False
            else:
                print("Try按钮不可用")
                return False
        except Exception as e:
            print(f"查找Try按钮失败: {e}")
            return False
        
        # 2. 查找并点击MP3下载按钮
        try:
            mp3_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'MP3') or contains(text(), 'Full track') or contains(text(), '.MP3')]")
            mp3_button = None
            
            for element in mp3_elements:
                try:
                    parent = element.find_element(By.XPATH, "./ancestor-or-self::*[self::button or self::div[@role='button'] or self::a][1]")
                    if parent and parent.is_displayed():
                        mp3_button = parent
                        break
                except:
                    continue
            
            if mp3_button:
                if self.safe_click_element(mp3_button):
                    self.humanized_delay(1, 2)
                else:
                    print("点击MP3按钮失败")
                    return False
            else:
                print("未找到MP3下载按钮")
                return False
                
        except Exception as e:
            print(f"查找MP3按钮时出错: {e}")
            return False
        
        # 3. 关闭网页弹窗
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "[role='dialog'] button[aria-label='Close']")
            
            if close_button and close_button.is_displayed() and close_button.is_enabled():
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                self.humanized_delay(0.5, 1)
                
                if self.safe_click_element(close_button):
                    self.humanized_delay(1, 2)
                else:
                    print("点击关闭按钮失败")
            else:
                print("未找到关闭按钮，请手动关闭网页弹窗")
                print("请手动点击弹窗右上角的 X 按钮关闭弹窗")
        except Exception as e:
            print(f"关闭弹窗时出错: {e}")
        
        return True
    
    def get_current_page_tracks(self):
        try:
            self.humanized_delay(1, 2)
            track_selectors = [
            "tbody tr:has(button[aria-label='Try'])",
            ]
            
            tracks = []
            for selector in track_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath选择器
                        tracks = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS选择器
                        tracks = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                    if tracks:
                        break
                except Exception as e:
                    print(f"选择器 '{selector}' 失败: {e}")
                    continue
            
            return tracks
            
        except Exception as e:
            print(f"获取音轨列表时出错: {e}")
            return []

    def download_all_music(self, total_pages=14, total_tracks=341):
        """下载所有音乐"""
        downloaded_count = 0
        current_page = 1
        
        print(f"开始下载 {total_tracks} 首音乐，共 {total_pages} 页")
        
        while current_page <= total_pages and downloaded_count < total_tracks:
            print(f"\n=== 处理第 {current_page} 页 ===")
            
            tracks = self.get_current_page_tracks()
            
            if not tracks:
                print(f"第 {current_page} 页没有找到音轨")
                break
            
            tracks_count = len(tracks)
            
            for i in range(tracks_count):
                if downloaded_count >= total_tracks:
                    break
                
                current_tracks = self.get_current_page_tracks()
                if i >= len(current_tracks):
                    print(f"音轨索引 {i} 超出范围，跳过")
                    break
                    
                track = current_tracks[i]
                track_number = downloaded_count + 1
                print(f"\n下载第 {current_page} 页的第 {i + 1} 首音乐（总第 {track_number} 首）")
                
                success = self.download_single_track(track, track_number)
                
                if success:
                    downloaded_count += 1
                    print(f"成功下载！进度: {downloaded_count}/{total_tracks}")
                else:
                    print(f"下载失败，跳过此音轨")
                
                self.humanized_delay(2, 5)
            
            # 当前页下载完毕，转到下一页 -- Cannot by now
            if current_page < total_pages and downloaded_count < total_tracks:
                if self.go_to_next_page():
                    current_page += 1
                    print(f"已转到第 {current_page} 页")
                else:
                    print("无法转到下一页，下载结束")
                    break
            else:
                break
        
        print(f"\n下载完成！共下载了 {downloaded_count} 首音乐")
        return downloaded_count
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    print("Shutterstock音乐下载器")
    print("=" * 50)
    
    downloader = ShutterstockMusicDownloader(browser="chrome")
    
    print("正在连接到现有浏览器会话...")
    if not downloader.connect_to_existing_browser():
        print("\n连接失败！")
        return
    
    print("\n开始自动下载...")
    downloaded = downloader.download_all_music()
    
    if downloaded > 0:
        print(f"成功下载了 {downloaded} 首音乐")
        print(f"文件保存在: {downloader.download_dir}")
    else:
        print("没有下载任何音乐")

if __name__ == "__main__":
    main()