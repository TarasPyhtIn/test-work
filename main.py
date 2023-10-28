from telebot import TeleBot, types
import pandas as pd
import matplotlib.pyplot as plt

bot = TeleBot("6855421449:AAEpWWL-TrEdVWnGEiuSUhmVolGYa9mab-U")

def check_buy(buys, buy_price, buy_proc, capital):
    if price <= buy_price:
        if price <= capital:
            print("    @@ buy: ", price,"  %:", buy_proc)
            order_info=[]
            buys+=1
            buy_price = price-(price/100*buy_proc)
            sell_price= price+(price/100*0.05)

            #рахування гррошей V
            capital -= price
            buy_price = price

            order_info=[buys, sell_price, buy_price]
            order_list.append(order_info)
        else:
            print("гроші все, закінчилися")
    else:
        print('XX')    
    return buys, buy_price, capital
        
def check_sell(order_listf, sels, capital):
    for i in order_listf:
        if price > i[1]:
            print('    $$ sell: buy price=', i[2], ' sell price=', price)
            order_listf.remove(i)
            sels+=1
            #рахування гррошей V
            capital += price
    return sels, capital

def trading(capital, historical_base):
    t = 0

    capital_list=[]
    capital_list.append(capital)

    start_capital = capital 
    capital1 =capital2 = capital3 = capital/3

    buys = 0
    sels = 0

    db=pd.read_csv(historical_base)
    
    print(db.loc[t, db.columns[0]])
    global price
    global start_price
    under_price = start_price = price = db.loc[t, db.columns[1]]

    price_list = []
    price_list.append(price)

    global order_list
    order_list=[]

    buy_proc1 = 0.01
    buy_proc2 = 0.02
    buy_proc3 = 0.04

    buy_price1 = start_price-(start_price/100*buy_proc1)
    buy_price2 = start_price-(start_price/100*buy_proc2)
    buy_price3 = start_price-(start_price/100*buy_proc3)

    while t != len(db.index)-2:

        print(str(t)+'--->'+str(price))
        buys, buy_price1, capital1 = check_buy(buys, buy_price1, buy_proc1, capital1)#перевірка чи можна купити акцію/крипту
        buys, buy_price2, capital2 = check_buy(buys, buy_price2, buy_proc2, capital2)#перевірка чи можна купити акцію/крипту
        buys, buy_price3, capital3 = check_buy(buys, buy_price3, buy_proc3, capital3)#перевірка чи можна купити акцію/крипту

        sels, capital1 = check_sell(order_list, sels, capital1)#перевірка чи можна продати
        sels, capital2 = check_sell(order_list, sels, capital2)#перевірка чи можна продати
        sels, capital3 = check_sell(order_list, sels, capital3)#перевірка чи можна продати

        if price < under_price:
            under_price = price

        capital_list.append((capital1+capital2+capital3))

        t+=1
        try:
            price = db.loc[t, db.columns[1]]
        except:
            t = len(db.index)-1

    profit = (capital-start_capital)/(start_capital/100)

    graph_db = plt.plot(capital_list)
    plt.savefig('graph_photo.png')

    print(len(db.index))
    capital_profit= "початковий капітал був:" + str(start_capital) + "$ \nзараз капітал складає:" + str(round(int(capital1)+int(capital2)+int(capital3), 2)) + "$" + "\nбуло куплено: "+str(buys)+" біткоїнів, продано: "+ str(sels)+" відсоток прибутку:"+str(round(profit, 2))+"%\nнайнижча ціна була:"+str(under_price)
    print(capital_profit)
    return capital_profit, graph_db

##############################
##  under is telegram bot   ##
##############################

capital = 0
db = ''

@bot.message_handler(commands=['start', "restart"])
def send_info(message):
    markup = types.InlineKeyboardMarkup()
    set_capital = types.InlineKeyboardButton("почати тестувати", callback_data='cliced!')
    markup.add(set_capital)

    bot.send_message(message.chat.id, "вітаю, я бот для трейдингу криптовалютами, нажми на кнопку що б почати тестувати мене", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data == 'cliced!':
        bot.send_message(query.from_user.id, "відправ мені історичні данні в CSV форматі, але бажано не великий за розміром")
        @bot.message_handler(content_types=['document'])
        def adding_the_db(message):
            global db
            db = ''
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                file_name = f"C:/Users/Taras/code/test_work/{message.document.file_name}"  # Specify your desired directory here
                with open(file_name, 'wb') as new_file:
                    new_file.write(downloaded_file)

                bot.reply_to(message, f"чудово, данні я отримав")
                db = message.document.file_name
            except:
                bot.send_message(message.chat.id, "щось пішло не так, можливо файл за великий, спробуйте щераз використавши команди /start, /restart")
                send_info()

            bot.send_message(query.from_user.id, "напищіть скільки ви бажаєте встановити капіталу(починаючи з 90000 що бот міг купити хоча б один біткоїн інакше зе не має сенсу)")
            @bot.message_handler(func=lambda message: message.text)
            def button_foof(message):
                if int(message.text):
                    global capital
                    global db
                    global graph_db

                    messagetext ='чудово, '+str(message.text) + "$ отримано"
                    bot.send_message(message.chat.id, messagetext)
                    capital = int(message.text)
                    
                    kw = types.InlineKeyboardMarkup()
                    kwg = types.InlineKeyboardButton("графік капіталу", callback_data='graph!')
                    set_capital = types.InlineKeyboardButton("почати тестувати", callback_data='cliced!')
                    kw.add(kwg, set_capital)

                    bot.send_message(message.chat.id, 'рахую...')
                    massege_text, graph_db = trading(capital, db)
                    bot.send_message(message.chat.id, massege_text, reply_markup=kw)


    elif data == 'graph!':
        kw = types.InlineKeyboardMarkup()
        kwg = types.InlineKeyboardButton("графік капіталу", callback_data='graph!')
        set_capital = types.InlineKeyboardButton("почати тестувати", callback_data='cliced!')
        kw.add(set_capital)
        graph_photo=r"C:\Users\Taras\code\test_work\graph_photo.png"
        
        bot.send_photo(query.from_user.id, open(graph_photo, 'rb'), "грфік", reply_markup=kw)

bot.infinity_polling()