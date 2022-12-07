while True:
                resp = r.post('https://api.scrolller.com/api/v2/graphql', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
                data_images = json.loads(resp.text)
                if data_images['data']['getSubreddit'] != None:
                    for item in data_images['data']['getSubreddit']['children']['items']:
                        #print(c)
                        url = item['mediaSources'][len(item['mediaSources'])-1]['url']
                        #print(url)
                        
                        page = r.get(url)

                        f_ext = os.path.splitext(url)[-1]
                        imgname = url.split('.com/')[1].replace('.jpg', '').replace('.png', '').replace('.webm', '').replace('.gif', '')

                        if page.status_code == 200:
                            with Image.open(io.BytesIO(page.content)) as img:
                                fc = file_check(img, imgname, f_ext, page)
                                if fc:
                                    c+=1
                        if c >= Whiles:
                            break
                    if c >= Whiles:
                        break