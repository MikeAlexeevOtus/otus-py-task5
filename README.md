# python epoll http server

## архитектура

сервер состоит из мастер процесса и нескольких воркеров

В воркере через epoll происходит опрос событий на серверном сокете (main_loop.py)
Когда происходит новое подключение, вызывается accept и в epoll регистрируется fd этого сокета
Когда в сокете появляются данные, готовые для чтения, они вычитываются в буффер объекта Request

Когда заголовки запроса прочитаны (для формирования ответа пейлоад не нужен), опрос событий этого сокета переключается на EPOLLOUT, чтобы получать уведомления, когда сокет готов для отправки ответа

Чтобы не блокироваться на файловых операциях при формировании ответа, эта часть вынесена в поток
Добавлена очередь, куда попадают дескрипторы сокетов, готовых к записи
Поток разгребает эту очередь.

Чтобы не получить несколько раз уведомление из epoll о том, что сокет готов к записи, пока из треда еще не случилась запись, после формирования задания для очереди основной тред отписывается от событий epoll для этого сокета. Подписка восстанавливается из потока, когда отправлен фрагмент ответа

## запуск

Для запуска нужен python 3

`python3 src/httpd.py -r http-test-suite  -w4`

Также есть параметры --addr и --port, --debug

## бенчмарк

замер делался с утилитой ab

`ab -n 50000 -c 100 -r http://127.0.0.1:8080/`

При одном воркере:

```
Concurrency Level:      100
Time taken for tests:   7.073 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      6050000 bytes
HTML transferred:       0 bytes
Requests per second:    7069.55 [#/sec] (mean)
Time per request:       14.145 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
Transfer rate:          835.37 [Kbytes/sec] received
```

При 4 воркерах:

```
Concurrency Level:      100
Time taken for tests:   2.418 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      6050000 bytes
HTML transferred:       0 bytes
Requests per second:    20680.69 [#/sec] (mean)
Time per request:       4.835 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)
Transfer rate:          2443.71 [Kbytes/sec] received
```

## известные проблемы

при нескольких воркерах (больше, чем 2) возникает ошибка:

`RuntimeError: request is not read yet`

выглядит так, будто сервер пытается отдать ответ до того, как запрос прочитан полностью
На 50000 запросов происходит около 5 таких ошибок
