from demo import redis_client
import json
import redis


class RedisUtil:
    @staticmethod
    def set_key(key, value, ex=None):
        """设置键值，可选设置过期时间(秒)"""
        redis_client.set(key, value, ex=ex)

    @staticmethod
    def get_key(key):
        """获取键值"""
        return redis_client.get(key)

    @staticmethod
    def incr_counter(key):
        """自增计数器"""
        return redis_client.incr(key)

    @staticmethod
    def delete_key(key):
        """删除键"""
        return redis_client.delete(key)
    @staticmethod
    def get_all_keys():
        """获取所有键"""
        return redis_client.keys("*")

    @staticmethod
    def enqueue(queue_name, item):
        """入队 (序列化数据)"""
        try:
            return redis_client.lpush(queue_name, json.dumps(item))
        except redis.RedisError as e:
            raise RuntimeError(f"Redis入队失败: {str(e)}")

    @staticmethod
    def dequeue(queue_name, timeout=30):
        """阻塞式出队 (反序列化数据)"""
        try:
            # 返回格式: (queue_name, data) 或 None
            result = redis_client.brpop(queue_name, timeout=timeout)
            return json.loads(result[1]) if result else None
        except redis.RedisError as e:
            raise RuntimeError(f"Redis出队失败: {str(e)}")

    @staticmethod
    def get_queue_length(queue_name):
        """获取队列长度"""
        return redis_client.llen(queue_name)

    @staticmethod
    def move_data_between_queues(source_queue, target_queue, timeout=0):
        """使用BRPOPLPUSH从source队列弹出数据并推送到target队列"""
        try:
            # 使用BRPOPLPUSH进行阻塞式操作
            data = redis_client.brpoplpush(source_queue, target_queue, timeout)
            if data:
                print(f"数据成功转移: {data.encode('utf-8')}")
                return True
            else:
                print("队列为空或操作超时")
                return False
        except redis.RedisError as e:
            print(f"Redis操作失败: {str(e)}")
            return False
