'''
Oct 04 21:35:43 ip-172-31-10-97 gunicorn[15040]: Element found: 시간 메뉴
Oct 04 21:35:43 ip-172-31-10-97 gunicorn[15040]: 시간 메뉴 클릭 완료
Oct 04 21:35:45 ip-172-31-10-97 gunicorn[15040]: 시간 메뉴 클릭을 기다리는 중 타임아웃 발생
Oct 04 21:35:45 ip-172-31-10-97 gunicorn[15040]: Trying to click on element: 1시간 옵션 with XPath: //cq-item[./translate[text()='1시간']]
Oct 04 21:35:45 ip-172-31-10-97 gunicorn[15040]: Element found: 1시간 옵션
Oct 04 21:35:45 ip-172-31-10-97 gunicorn[15040]: 1시간 옵션 클릭 완료
Oct 04 21:35:47 ip-172-31-10-97 gunicorn[15040]: 1시간 옵션 클릭을 기다리는 중 타임아웃 발생
Oct 04 21:35:47 ip-172-31-10-97 gunicorn[15040]: Trying to click on element: 차트설정 with XPath: //*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[2]/span
Oct 04 21:35:47 ip-172-31-10-97 gunicorn[15040]: Element found: 차트설정
Oct 04 21:35:48 ip-172-31-10-97 gunicorn[15040]: 차트설정 클릭 완료
Oct 04 21:35:50 ip-172-31-10-97 gunicorn[15040]: 차트설정 클릭을 기다리는 중 타임아웃 발생
Oct 04 21:35:50 ip-172-31-10-97 gunicorn[15040]: 다크테마 옵션 클릭 완료

여기까지 진행됨. 그런데 차트 설정창이 닫히지 않았네. 여기서부터 큰 문제가 발생했네.
아래는 내가 새로 xpath를 찾아본거야
시간메뉴 : //*[@id="fullChartiq"]/div/div/div[1]/div/div/cq-menu[1]/span/cq-clickable
1시간 : //*[@id="fullChartiq"]/div/div/div[1]/div/div/cq-menu[1]/cq-menu-dropdown/cq-item[8]/translate
차트설정 : //*[@id="fullChartiq"]/div/div/div[1]/div/div/cq-menu[2]/span/translate
지표 : //*[@id="fullChartiq"]/div/div/div[1]/div/div/cq-menu[3]/span/translate

'''

    # #ec2 서버용
    # def _capture_and_save_screenshot(self):
    #     try:
    #         # 페이지가 완전히 로드될 때까지 대기
    #         WebDriverWait(self.driver, 20).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="fullChartiq"]/div/div'))
    #         )

    #         # 차트 요소 찾기
    #         chart_element = self.driver.find_element(By.XPATH, '//*[@id="fullChartiq"]/div/div')

    #         # 차트 요소의 크기 가져오기
    #         size = chart_element.size
            
    #         # 창 크기를 차트 크기에 맞게 조정 (높이에 여유를 두기 위해 100px 추가)
    #         self.driver.set_window_size(size['width'], size['height'] + 100)

    #         # 차트 요소의 위치 정보 가져오기
    #         location = chart_element.location

    #         # 전체 스크린샷 찍기
    #         png = self.driver.get_screenshot_as_png()

    #         # 이미지 처리
    #         im = Image.open(io.BytesIO(png))
    #         left = location['x']
    #         top = location['y']
    #         right = left + size['width']
    #         bottom = top + size['height']

    #         # 차트 부분만 크롭
    #         im = im.crop((left, top, right, bottom))

    #         # 이미지 저장
    #         current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f"chart_screenshot_{current_time}.png"
    #         save_dir = os.path.join(settings.MEDIA_ROOT, 'capture_chart')
    #         os.makedirs(save_dir, exist_ok=True)
    #         file_path = os.path.join(save_dir, filename)
    #         im.save(file_path)

    #         logger.info(f"스크린샷이 저장되었습니다: {file_path}")
    #         image_url = f"{settings.MEDIA_URL}capture_chart/{filename}"
    #         return image_url
    #     except Exception as e:
    #         logger.error(f"스크린샷 캡처 및 저장 중 오류 발생: {e}")
    #         return None
