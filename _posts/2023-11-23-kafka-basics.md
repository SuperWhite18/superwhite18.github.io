---
title: "Kafka 基本原理"
date: 2023-11-23
tags: [Kafka]
---

## 一.定义

Kafka是一种高吞吐量的分布式发布订阅消息系统，可以处理消费者规模的网站中的所有动作流数据，具有高性能，持久化，多副本备份，横向扩展能力等。

## 二.基础架构及术语
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/73a29daed2e1cbe6ce635fc0850822e6.png' | relative_url }})
**Producer：** 生产者，消息的生产者，消息的入口
**Kafka cluster：**
**Broker：** brocker是kafka的实例，每个服务器上有一个或多个kafka的实例，每个broker对应一台服务器，每个kafka集群内的broker都有一个编号，如broker0，broker1等
**Topic：** 消息的主题，可以理解为分类，kafka的数据就保存在topic。在每个broker上可以创建多个topic
**Partiton：** Topic的分区，每个topic有多个分区，分区的作用做负载，提高kafka的吞吐。同一个topic在不同的分区的数据是不重复的，partition的表现形式就是一个一个的文件夹
**Replication：** 每一个分区都有多个副本，主分区也就是leader故障的时候就会选择一个备胎（follower）上位升级成一个leader，在kafka中默认副本的最大数量是10个，副本的数量不能大于broker的数量，follower和leader绝对是在不同的机器，同一机器对同一个分区也只能存放一个副本
**Message：** 每一条发送的消息主体
**Consumer：** 消费者，即消息的消费方，是消息的出口
**Consumer Group：** 我们可以将多个消费者组成一个消费者组，在kafka的设计中同一个分区的数据只能被消费者组中的某一个消费者消费。同一个消费者组的消费者可以消费同一个topic的不同分区的数据，这也是为了提高kafka的吞吐量
**Zookeeper：** kafka集群依赖zookeper来保存集群的元信息，保证系统的可用性

## 三.工作流程分析
## 3.1发送数据
生产者在写入数据的时候永远先找leader，不会直接将数据写入备胎
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/a94b25de8ebb8bbd22e502837b24d78b.png' | relative_url }})
消息写入leader之后，follower是主动去找leader进行同步，生产者把数据push到broker，每条消息追加到分区中，顺序写入磁盘，写入磁盘的顺序如下：
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/4f79ad0a61a883b93c3272a1fbe7b6f2.png' | relative_url }})
**所以kafka为什么要做分区有如下几个目的：**

 - 方便扩展，一个topic可以有多个partition，所以我们通过扩展机器去轻松的应对逐渐增长的数据量
 - 提高并发，以partition为读写单位，可以多个消费者进行同时消费，提高消息处理效率

**那么在Kafka中，某个topic有多个partition，生产者怎么判断将数据发往哪个partition？**

 1. partition在写入的时候是可以指定需要写入的partition，如果有指定，则写入对应的partition
 2. 如果没有指定partition，但是设置了数据的key值，则会根据key值的hash一个对应的partition
 3. 如果前两者都没有，则轮询选择

**在生产者写数据时如何保证数据不丢失呢？**

 1. 通过ACK应答机制，在生产者向队列写入数据时可以设置参数来确定是否接收到数据，这个参数数据可以设置为0
 2. 0代表producer往集群发送数据不需要等到集群的返回，不确保消息发送成功。安全性最低但是效率最高
 3. 1代表producer往集群发送数据只要leader应答就可以发送下一条，只确保leader发送成功
 4. all代表producer往集群发送数据需要所有的follower都完成从leader的同步才会发送下一条，确保leader发送成功和所有的副本都完成备份。安全性最高，但是效率最低

**如果生产者向不存在的topic分区中写入数据，Kafka会自动创建topic，分区和副本的数量根据默认配置都是1**

## 3.2保存数据
producer将数据写入后，集群就要对数据进行保存了，Kafka是将数据保存在磁盘中，Kafka会单独开辟一块磁盘空间，顺序写入数据（效率比随机写入高）
### 3.2.1 partition结构
每个topic都可以分为一个或多个partition，如果topic理解起来抽象，那么partition比较具体，本质在服务器上就是一个一个的文件夹，每一个partition文件夹下面会有多个segment文件，每组segment文件又包含.index文件、.log文件、.timeindex文件，**log文件存储message，index和timeindex为索引文件，用于检索消息**
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/895e170c28f008130fa883e853d317a9.png' | relative_url }})
如上图，这个partition有三组segment文件，每个log文件的大小是一样的，但是存储的message数量是不一定相等的（每条的message大小不一致）。文件的命名是以该segment最小offset来命名的，如000.index存储offset为0~368795的消息，kafka就是利用分段+索引的方式来解决查找效率的问题。
### 3.2.2 message结构
log文件时存储message的地方，那么producer在向kafka写入的也是一条条的message，那么存储在log的message是什么样子的，消息主要包含消息体、消息大小、offset、压缩类型等，主要关注如下三点：

 1. offset：是一个占8byte的有序id号，可以确定每条消息在partition内的位置
 2. 消息大小：消息大小占用4byte，描述消息大小
 3. 消息体：消息体存放的是实际的消息数据，占用的空间根据具体的消息而不一样

### 3.2.3 存储策略
无论消息是否被消费，kafka都会保存所有的消息，那么对于旧数据有什么淘汰策略呢？
 

 1. 时间策略：默认配置168小时（7天）
 2. 大小策略：默认是1073741824
 
需要注意的是，kafka读取特定消息的时间复杂度是O(1)，所以这里删除过期的文件并不会提高kafka的性能

### 3.2.4 消费数据
消息存储在log文件后，消费者可以开始消费了，多个消费者组成一个消费者组，每个消费者组都有一个组id，同一个消费者组的消费者可以消费同一topic下不同分区的数据，但是不会消费同一分区的数据！
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/fcbadd707c3135803a412c94d24581eb.png' | relative_url }})
上图中消费者组内的消费者小于partition，3个消费者，4个分区，这样就会出现消费者消费多个partition数据的情况，可能消费不过来，简单说就是供大于求，如消费者数大于分区数，是否会出现供不应求的情况，这种情况是不会出现的，多出来的消费者是不消费任何partition的数据的，所以在实际应用中，建议消费者的数量和分区数量一致。
****
在保存数据那里说过，partition划分为多组segment，每个segment又包含几个文件，存放的每条message包含offset、消息大小、消息体等。那么在查找过程中，每次提到segment和offset，比如现在想要查找一个offset为368801的message，该怎么找呢？
![在这里插入图片描述]({{ '/assets/images/posts/2023-11-23-kafka-basics/86e5ecf47b548fe1e042d56dd4674244.png' | relative_url }})

 1. 先找到offset的368801message所在的segment文件（二分法）
 2. 打开找到的segment中的.index文件（368796.index，起始偏移量为368796+1，我们要查找的offset为368801的message在该index内的偏移量为368796+5=368801，所以这里要查找的相对offset为5）。由于该文件采用的是稀疏索引的方式存储着相对offset及对应message物理偏移量的关系，所以直接找相对offset为5的索引找不到，这里同样利用二分法查找相对offset小于或者等于指定的相对offset的索引条目中最大的那个相对offset，所以找到的是相对offset为4的这个索引。
 3. 根据找到的相对offset为4的索引确定message存储的物理偏移位置为256。打开数据文件，从位置为256的那个地方开始顺序扫描直到找到offset为368801的那条Message
 4. 这套机制是建立在offset为有序的基础上，利用segment+有序offset+稀疏索引+二分查找+顺序查找等多种手段来高效的查找数据！至此，消费者就能拿到需要处理的数据进行处理了。那每个消费者又是怎么记录自己消费的位置呢？在早期的版本中，消费者将消费到的offset维护zookeeper中，consumer每间隔一段时间上报一次，这里容易导致重复消费，且性能不好！在新的版本中消费者消费到的offset已经直接维护在kafk集群的__consumer_offsets这个topic中

