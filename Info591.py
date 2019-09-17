import sys, os, time, requests as req
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as b4s
import selenium.common.exceptions as selExcept

# 591爬蟲類別，用來取得法拍屋資訊
class Info591:
    county = ''
    section = ''
    price = ''

    def __init__(self, _county, _section, _price):
        if _county == None or _county == '': raise Exception('縣市代碼不可為空')
        self.county, self.section, self.price = _county, _section, _price

    # 取得頁面中符合條件第一個元件
    def getElementByLocator(self, driver, typeBy, slocator):
        wait = WebDriverWait(driver, 20, 0.5)
        sErr = "Can't find element"
        return wait.until(EC.presence_of_element_located((typeBy, slocator)), sErr)

    # 取得頁面中符合條件所有元件
    def getAllElementsByLocator(self, driver, typeBy, slocator):
        wait = WebDriverWait(driver, 20, 0.5)
        sErr = "Can't find element"
        return wait.until(EC.presence_of_all_elements_located((typeBy, slocator)), sErr)

    # 取得元件中的元件
    def getInnerElementByXPath(self, parent, xpath):
        try:
            return parent.find_element_by_xpath(xpath)
        except:
            return

            # 取代換行字元

    def replaceRtn(self, sText, sNewStr):
        return sText.replace('\n', sNewStr)

    def getInfo591(self):

        # 輸出結果
        lstOut = []
        # 讀取該頁資料
        loadPage = True
        # 頁數
        iPageCnt = 0
        # ///xpath///
        # 房屋清單的的主框
        xpHouseFrame = "//div[contains(@class, 'houseList-item-main') and contains(@class, 'oh')]"
        # 標題
        xpTitle = "div[@class='houseList-item-title']"
        # 熱銷建案
        xpHot = "span[contains(@class, 'houseList-item-title-label')]"
        # 房屋明細url
        xpDtlUrl = "div[@class='houseList-item-title']/a"
        # 屬性
        xpAttr = "div[contains(@class, 'houseList-item-attr-row')]"
        # 地址
        xpAddr = "div[contains(@class, 'houseList-item-address-row')]"
        # 經銷商/房仲公司資訊
        xpCmp = "div[contains(@class, 'houseList-item-company-row')]"
        # 其他資訊
        xpTags = "div[@class='houseList-item-tags']"
        # 價格
        xpPrice = "../div[contains(@class, 'houseList-item-right')]/div[contains(@class, 'houseList-item-price')]/em"
        # 每坪單價
        xpUPrice = "../div[contains(@class, 'houseList-item-right')]/div[contains(@class, 'houseList-item-unitprice')]"
        # 下一頁
        xpPageNext = "//a[contains(@class, 'pageNext')]"
        # 更新時間
        xpUpdTime = "//span[@class='detail-info-span'][3]"

        sUrl = 'https://sale.591.com.tw/?shType=list&kind=22&order=price_asc'
        sUrl += '&regionid=' + self.county
        if self.section != None and self.section != '': sUrl += '&section=' + self.section
        if self.price != None and self.price != '': sUrl += '&price=' + self.price
        # 打開瀏覽器，並到登入的網址
        driver = webdriver.Chrome()
        driver.get(sUrl)
        driver.minimize_window()
        # driver.implicitly_wait(20)

        try:
            while loadPage:
                # 該頁所有房屋物件
                elems = self.getAllElementsByLocator(driver, By.XPATH, xpHouseFrame)
                iPageCnt += 1

                for i in range(0, len(elems)):
                    elem = elems[i]
                    title = self.getInnerElementByXPath(elem, xpTitle)
                    hot = self.getInnerElementByXPath(title, xpHot)
                    attr = self.getInnerElementByXPath(elem, xpAttr)
                    addr = self.getInnerElementByXPath(elem, xpAddr)
                    cmp = self.getInnerElementByXPath(elem, xpCmp)
                    tags = self.getInnerElementByXPath(elem, xpTags)
                    price = self.getInnerElementByXPath(elem, xpPrice)
                    uPrice = self.getInnerElementByXPath(elem, xpUPrice)
                    dtlUrl = self.getInnerElementByXPath(elem, xpDtlUrl)

                    if hot == None and dtlUrl != None:
                        lstOut.append(title.text + '|' + dtlUrl.get_attribute('href'))
                        otherPage = req.get(dtlUrl.get_attribute('href'))
                        soup = b4s(otherPage.text, 'html.parser')
                        updTime = soup.select('.ft-rt')
                        if len(updTime) > 0: lstOut.append(updTime[0].text.split('：')[1])
                    else:
                        lstOut.append(title.text)

                    if price != None:
                        if uPrice != None:
                            lstOut.append(price.text + '萬|' + uPrice.text)
                        else:
                            lstOut.append(price.text + '萬|')

                    if attr != None: lstOut.append(self.replaceRtn(attr.text, '|'))
                    if addr != None: lstOut.append(self.replaceRtn(addr.text, ''))
                    if cmp != None: lstOut.append('公司:' + cmp.text)
                    if tags != None: lstOut.append(self.replaceRtn(tags.text, '\t'))

                    if i < (len(elems) - 1): lstOut.append('==================')
                lstOut.append('==================Page {0} end=================='.format(iPageCnt))
                # 是否還有下一頁
                pageNext = self.getElementByLocator(driver, By.XPATH, xpPageNext)
                loadPage = pageNext.get_attribute('class').find('last') == -1
                if loadPage:
                    pageNext.click()
                    time.sleep(3)
                    # driver.implicitly_wait(10)
                    # while driver.execute_script("return document.readyState") != 'complete':time.sleep(1)

            driver.close()
        except selExcept.NoSuchWindowException:
            lstOut.append('強制中止')
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # lstOut.append('{}:{}:{}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
            lstOut.append('{}:{}:{}'.format(exc_type, fname, exc_tb.tb_lineno))

        return lstOut