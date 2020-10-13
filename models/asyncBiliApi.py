# -*- coding: utf-8 -*-
from aiohttp import ClientSession

class asyncBiliApi(object):
    '''B站异步api'''
    def __init__(self):

        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108","Referer": "https://www.bilibili.com/",'Connection': 'keep-alive'}
        
        self._session = ClientSession(
                headers = headers
                )
        
    async def login_by_cookie(self, cookieData) -> bool:
        '''
        登录并获取账户信息
        cookieData dict 账户cookie
        '''
        self._session.cookie_jar.update_cookies(cookieData)
        ret = await self.getWebNav()
        if ret["code"] != 0:
            return False

        if 'bili_jct' in cookieData:
            self._bili_jct = cookieData["bili_jct"]
        else:
            self._bili_jct = ''

        self._name = ret["data"]["uname"]
        self._uid = ret["data"]["mid"]
        self._vip = ret["data"]["vipType"]
        self._level = ret["data"]["level_info"]["current_level"]
        self._verified = ret["data"]["mobile_verified"]
        self._coin = ret["data"]["money"]
        self._exp = ret["data"]["current_exp"]

        code = (await self.likeCv(7793107))["code"]
        if code != 0 and code != 65006 and code != -404:
            import warnings
            warnings.warn(f'{self._name}:账号异常，请检查bili_jct参数是否有效或本账号是否被封禁')

        return True

    @property
    def myexp(self) -> int:
        '''获取登录的账户的经验'''
        return self._exp

    @property
    def mycoin(self) -> int:
        '''获取登录的账户的硬币数量'''
        return self._coin

    @property
    def vipType(self) -> int:
        '''获取登录的账户的vip类型'''
        return self._vip
    
    @property
    def name(self) -> str:
        '''获取登录的账户用户名'''
        return self._name

    @property
    def uid(self) -> int:
        '''获取登录的账户uid'''
        return self._uid

    async def getWebNav(self) -> dict:
        '''取导航信息'''
        url = "https://api.bilibili.com/x/web-interface/nav"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getReward(self) -> dict:
        '''取B站经验信息'''
        url = "https://account.bilibili.com/home/reward"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret
    
    async def likeCv(self, 
                     cvid: int, 
                     type=1) -> dict:
        '''
        点赞专栏
        cvid int 专栏id
        type int 类型
        '''
        url = 'https://api.bilibili.com/x/article/like'
        post_data = {
            "id": cvid,
            "type": type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def vipPrivilegeReceive(self, type=1) -> dict:
        '''领取B站大会员权益'''
        url = 'https://api.bilibili.com/x/vip/privilege/receive'
        post_data = {
            "type": type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getUserWallet(self, platformType=3) -> dict:
        '''获取账户钱包信息'''
        url = 'https://pay.bilibili.com/paywallet/wallet/getUserWallet'
        post_data = {
            "platformType": platformType
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def elecPay(self, uid: int, num=50) -> dict:
        '''
        用B币给up主充电
        uid int up主uid
        num int 充电电池数量
        '''
        url = 'https://api.bilibili.com/x/ugcpay/trade/elec/pay/quick'
        post_data = {
            "elec_num": num,
            "up_mid": uid,
            "otype": 'up',
            "oid": uid,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveSign(self) -> dict:
        '''B站直播签到'''
        url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveGetRecommendList(self) -> dict:
        '''B站直播获取首页前10条直播'''
        url = f'https://api.live.bilibili.com/relation/v1/AppWeb/getRecommendList'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveGetRoomInfo(self,
                               room_id: int) -> dict:
        '''
        B站直播获取房间信息
        room_id int 房间id
        '''
        url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveGiftBagList(self) -> dict:
        '''B站直播获取背包礼物'''
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveBagSend(self,
                           biz_id,
                           ruid,
                           bag_id, 
                           gift_id, 
                           gift_num, 
                           storm_beat_id=0, 
                           price=0, 
                           platform="pc") -> dict:
        '''
        B站直播送出背包礼物
        biz_id int 房间号
        ruid int up主的uid
        bag_id int 背包id
        gift_id int 背包里的礼物id
        gift_num int 送礼物的数量
        storm_beat_id int
        price int 礼物价格
        platform str 平台
        '''
        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        post_data = {
            "uid": self._uid,
            "gift_id": gift_id,
            "ruid": ruid,
            "send_ruid": 0,
            "gift_num": gift_num,
            "bag_id": bag_id,
            "platform": platform,
            "biz_code": "live",
            "biz_id": biz_id,
            #"rnd": rnd, #直播开始时间
            "storm_beat_id": storm_beat_id,
            "price": price,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def coin(self, 
             aid: int, 
             num=1, 
             select_like=1) -> dict:
        '''
        给指定av号视频投币
        aid int 视频av号
        num int 投币数量
        select_like int 是否点赞
        '''
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return aid, ret

    async def report(self, 
                     aid, 
                     cid, 
                     progres) -> dict:
        '''
        B站上报视频观看进度
        aid int 视频av号
        cid int 视频cid号
        progres int 观看秒数
        '''
        url = "http://api.bilibili.com/x/v2/history/report"
        post_data = {
            "aid": aid,
            "cid": cid,
            "progres": progres,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def share(self, 
                    aid) -> dict:
        '''
        分享指定av号视频
        aid int 视频av号
        '''
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {
            "aid": aid,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def xliveGetStatus(self) -> dict:
        '''B站直播获取金银瓜子状态'''
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def silver2coin(self) -> dict:
        '''银瓜子兑换硬币'''
        url = "https://api.live.bilibili.com/pay/v1/Exchange/silver2coin"
        post_data = {
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getRegions(self, 
                         rid=1, 
                         num=6) -> dict:
        '''
        获取B站分区视频信息
        rid int 分区号
        num int 获取视频数量
        '''
        url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaClockIn(self, 
                     platform="android") -> dict:
        '''
        模拟B站漫画客户端签到
        platform str 平台
        '''
        url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
        post_data = {
            "platform": platform
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaGetPoint(self) -> dict:
        '''获取漫画积分'''
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/GetUserPoint'
        async with self._session.post(url, json={}, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaShopExchange(self, 
                                product_id: int, 
                                point: int, 
                                product_num=1) -> dict:
        '''
        漫画积分商城兑换
        product_id int 商品id
        point int 商品需要积分数量
        product_num int 兑换商品数
        '''
        url = f'https://manga.bilibili.com/twirp/pointshop.v1.Pointshop/Exchange'
        post_data = {
            "product_id": product_id,
            "point": point,
            "product_num": product_num
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaGetVipReward(self) -> dict:
        '''获取漫画大会员福利'''
        url = 'https://manga.bilibili.com/twirp/user.v1.User/GetVipReward'
        async with self._session.post(url, json={"reason_id":1}, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaComrade(self, 
                           platform="web") -> dict:
        '''
        站友日漫画卷兑换查询
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/activity.v1.Activity/Comrade?platform={platform}'
        async with self._session.post(url, json={}, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaPayBCoin(self, 
                            pay_amount: int, 
                            product_id=1, 
                            platform='web') -> dict:
        '''
        B币购买漫画
        pay_amount int 购买数量
        product_id int 购买商品id
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/pay.v1.Pay/PayBCoin?platform={platform}'
        post_data = {
            "pay_amount": pay_amount,
            "product_id": product_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaGetCoupons(self, 
                              not_expired=True, 
                              page_num=1, 
                              page_size=50, 
                              tab_type=1,
                              platform="web") -> dict:
        '''
        获取账户中的漫读劵信息
        not_expired bool
        page_num int 页数
        page_size int 每页大小
        tab_type int
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/user.v1.User/GetCoupons?platform={platform}'
        post_data = {
            "not_expired": not_expired,
            "page_num": page_num,
            "page_size": page_size,
            "tab_type": tab_type
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaListFavorite(self, 
                                page_num=1, 
                                page_size=50, 
                                order=1, 
                                wait_free=0, 
                                platform='web') -> dict:
        '''
        B站漫画追漫列表
        page_num int 页数
        page_size int 每页大小
        order int 排序方式
        wait_free int 显示等免漫画
        platform str 平台
        '''
        url = 'https://manga.bilibili.com/twirp/bookshelf.v1.Bookshelf/ListFavorite?platform={platform}'
        post_data = {
            "page_num": page_num,
            "page_size": page_size,
            "order": order,
            "wait_free": wait_free
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaDetail(self, 
                          comic_id: int, 
                          device='pc', 
                          platform='web') -> dict:
        '''
        获取漫画信息
        comic_id int 漫画id
        device str 设备
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device={device}&platform={platform}'
        post_data = {
            "comic_id": comic_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaGetEpisodeBuyInfo(self, 
                               ep_id: int, 
                               platform="web") -> dict:
        '''
        获取漫画购买信息
        ep_id int 漫画章节id
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisodeBuyInfo?platform={platform}'
        post_data = {
            "ep_id": ep_id
            }
        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def mangaBuyEpisode(self, 
                        ep_id: int, 
                        buy_method=1, 
                        coupon_id=0, 
                        auto_pay_gold_status=0, 
                        platform="web") -> dict:
        '''
        购买漫画
        ep_id int 漫画章节id
        buy_method int 购买参数
        coupon_id int 漫读劵id
        auto_pay_gold_status int 自动购买
        platform str 平台
        '''
        url = f'https://manga.bilibili.com/twirp/comic.v1.Comic/BuyEpisode?&platform={platform}'
        post_data = {
            "buy_method": buy_method,
            "ep_id": ep_id
            }
        if coupon_id:
            post_data["coupon_id"] = coupon_id
        if auto_pay_gold_status:
            post_data["auto_pay_gold_status"] = auto_pay_gold_status

        async with self._session.post(url, json=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def activityAddTimes(self, 
                               sid: str, 
                               action_type: int) -> dict:
        '''
        增加B站活动的参与次数
        sid str 活动的id
        action_type int 操作类型
        '''
        url = 'https://api.bilibili.com/x/activity/lottery/addtimes'
        post_data = {
            "sid": sid,
            "action_type": action_type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def activityDo(self, 
                         sid: str, 
                         type: int) -> dict:
        '''
        参与B站活动
        sid str 活动的id
        type int 操作类型
        '''
        url = 'https://api.bilibili.com/x/activity/lottery/do'
        post_data = {
            "sid": sid,
            "type": type,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def activityMyTimes(self, 
                              sid: str
                              ) -> dict:
        '''
        获取B站活动次数
        sid str 活动的id
        '''
        url = f'https://api.bilibili.com/x/activity/lottery/mytimes?sid={sid}'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getDynamic(self, 
                         type_list=268435455
                         ) -> dict:
        '''取B站用户动态数据'''
        async with self._session.get(f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={self._uid}&type_list={type_list}', verify_ssl=False) as r:
            ret = await r.json()
        cards = ret["data"]["cards"]
        for x in cards:
            yield x
        hasnext = True
        offset = cards[len(cards) - 1]["desc"]["dynamic_id"]
        while hasnext:
            async with self._session.get(f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history?uid={self._uid}&offset_dynamic_id={offset}&type={type_list}', verify_ssl=False) as r:
                ret = await r.json()
            hasnext = (ret["data"]["has_more"] == 1)
            #offset = ret["data"]["next_offset"]
            cards = ret["data"]["cards"]
            for x in cards:
                yield x
            offset = cards[len(cards) - 1]["desc"]["dynamic_id"]

    async def getDynamicDetail(self, 
                         dynamic_id: int
                         ) -> dict:
        '''
        获取动态内容
        dynamic_id int 动态id
        '''
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def dynamicReplyAdd(self, 
                              oid: int, 
                              message="", 
                              type=11, 
                              plat=1
                              ) -> dict:
        '''
        评论动态
        oid int 动态id
        message str 评论信息
        type int 评论类型
        plat int 平台
        '''
        url = "https://api.bilibili.com/x/v2/reply/add"
        post_data = {
            "oid": oid,
            "plat": plat,
            "type": type,
            "message": message,
            "csrf": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def dynamicRepostReply(self, 
                                 rid: int, 
                                 content="", 
                                 type=1, 
                                 repost_code=3000, 
                                 From="create.comment", 
                                 extension='{"emoji_type":1}'
                                 ) -> dict:
        '''
        转发动态
        rid int 动态id
        content str 转发评论内容
        type int 类型
        repost_code int 转发代码
        From str 转发来自
        extension str_json
        '''
        url = "https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/reply"
        post_data = {
            "uid": self._uid,
            "rid": rid,
            "type": type,
            "content": content,
            "extension": extension,
            "repost_code": repost_code,
            "from": From,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getMyDynamic(self, 
                           uid=0
                           ) -> 'generator':
        '''
        取B站用户的动态列表，生成器
        uid int B站用户uid
        '''
        if uid == 0:
            uid = self._uid
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&need_top=1&offset_dynamic_id='
        hasnext = True
        offset = ''
        while hasnext:
            async with self._session.get(f'{url}{offset}', verify_ssl=False) as r:
                ret = await r.json()
            hasnext = (ret["data"]["has_more"] == 1)
            if not 'cards' in ret["data"]:
                continue
            cards = ret["data"]["cards"]
            for x in cards:
                yield x
            offset = x["desc"]["dynamic_id_str"]

    async def removeDynamic(self, 
                            dynamic_id: int
                            ) -> dict:
        '''
        删除自己的动态
        dynamic_id int 动态id
        '''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic'
        post_data = {
            "dynamic_id": dynamic_id,
            "csrf_token": self._bili_jct
            }
        async with self._session.post(url, data=post_data, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def getLotteryNotice(self, 
                               dynamic_id: int
                               ) -> dict:
        '''
        取指定抽奖信息
        dynamic_id int 抽奖动态id
        '''
        url = f'https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={dynamic_id}'
        async with self._session.get(url, verify_ssl=False) as r:
            ret = await r.json()
        return ret

    async def __aenter__(self) -> 'aioBiliClient':
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def close(self) -> None:
        await self._session.close()