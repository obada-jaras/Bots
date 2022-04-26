import MetaTrader5 as mt5
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BoS = symbol = price = sl = tp1 = tp2 = tp3 = tp4 = tp5 = None
botToken=""













def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def catch_text(update, context):
    global update2
    update2 = update

    print(update2)

    text = str(update.message.text)
    update.message.reply_text(text)
    

    global BoS, price, symbol, sl, tp1, tp2, tp3, tp4, tp5
    BoS = symbol = "None"
    price = sl = tp1 = tp2 = tp3 = tp4 = tp5 = 0


    lines = text.upper().splitlines()
    for ln in lines:
 
        priceFlag = slFlag = tp1Flag = tp2Flag = tp3Flag = tp4Flag = tp5Flag = 0
        lineContent=ln.split()
        for word in lineContent:

            # value of BoS and price #
            if "SELL" in word:
                BoS = "SELL"
                priceFlag=1
            elif "BUY" in word:
                BoS = "BUY"
                priceFlag=1

            if "PRICE" in word:
                priceFlag=1

            if priceFlag == 1:
                if isfloat(word):
                    price = float(word)
            # -- end value of Bos and price --#
            

            # value of symbol #
            if word.isalpha() and len(word) == 6:
                symbol = word

            if "GOLD" in word:
                symbol = "XAUUSD"
            # -- end value of symbol -- #


            # value of stop lose #
            if "SL" in word or "LOSE" in word or "S/L" in word:
                slFlag=1

            if slFlag == 1:
                if isfloat(word):
                    sl = float(word)
            # -- end value of stop lose -- #


            # value of tp1 #
            if word == "TP" or word == "TP:" or "TP1" in word or word == "T/P" or "T/P1" in word:
                tp1Flag=1

            if tp1Flag == 1:
                if isfloat(word):
                    tp1 = float(word)
            # -- end value of tp1 -- #


            # value of tp2 #
            if "TP2" in word or "T/P2" in word:
                tp2Flag=1

            if tp2Flag == 1:
                if isfloat(word):
                    tp2 = float(word)
            # -- end value of tp2 -- #


            # value of tp3 #
            if "TP3" in word or "T/P3" in word:
                tp3Flag=1

            if tp3Flag == 1:
                if isfloat(word):
                    tp3 = float(word)
            # -- end value of tp3 -- #


            # value of tp4 #
            if "TP4" in word or "T/P4" in word:
                tp4Flag=1

            if tp4Flag == 1:
                if isfloat(word):
                    tp4 = float(word)
            # -- end value of tp4 -- #


            # value of tp5 #
            if "TP5" in word or "T/P5" in word:
                tp5Flag=1

            if tp5Flag == 1:
                if isfloat(word):
                    tp5 = float(word)
            # -- end value of tp5 -- #


    update.message.reply_text("BoS is: " + BoS + "\nprice: " + str(price) +"\nsymbol is: " +symbol)
    update.message.reply_text("Stop lose is: " + str(sl) + "\ntp1: " + str(tp1) +"\ntp2: " + str(tp2) + "\ntp3: " + str(tp3) +"\ntp4: " + str(tp4) + "\ntp5: " + str(tp5))
    print("BoS is: " + BoS + "\nprice: " + str(price) +"\nsymbol is: " + symbol)
    print("Stop lose is: " + str(sl) + "\ntp1: " + str(tp1) +"\ntp2: " + str(tp2) + "\ntp3: " + str(tp3) +"\ntp4: " + str(tp4) + "\ntp5: " + str(tp5) +"\n\n")





    errFlag=0

    if symbol == "None" or BoS == "None" or price == 0 or sl == 0 or tp1 == 0:
        update.message.reply_text("There is/are item/s without value/s")
        errFlag=1


    if BoS == "BUY":
        if sl>price or price>tp1:
            update.message.reply_text("BUY ERROR:\n     stop lose is greater than price\n     or price is greater than take profit")
            errFlag=1

        # if tp1>tp2 or tp2>tp3 or tp3>tp4 or tp4>tp5:
        #     update.message.reply_text("BUY: error in take profits, but order will done")


    elif BoS == "SELL":
        if sl<price or price<tp1:
            update.message.reply_text("SELL ERROR:\n     stop lose is less than price\n     or price is less than take profit")
            errFlag=1



    if errFlag == 1:
        update.message.reply_text("Error, Order will not be executed")

    else:
        update.message.reply_text("Sending order to MetaTrader5\n{} {} at {}\nStopLose: {}, and TakeProfit: {}".format(BoS, symbol, price, sl, tp1))
        print("Sending order to MetaTrader5\n{} {} at {}\nStopLose: {}, and TakeProfit: {}".format(BoS, symbol, price, sl, tp1))
            
        MetaTrader_Order(update, str(symbol), str(BoS), float(price), float(sl), float(tp1), float(0.02))



























def MetaTrader_Order(update, symbol, BoS, price, sl, tp, lot):

    # connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed")
        update.message.reply_text("initialize() failed")
        mt5.shutdown()

    

    # prepare the buy request structure
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        update.message.reply_text(symbol + "not found, can not call order_check()")

    
    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        update.message.reply_text(symbol + "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}) failed, exit",symbol)
            update.message.reply_text("symbol_select({}) failed, exit".format(symbol))


    
    deviation = 20



    if BoS == "SELL": 
        if price < mt5.symbol_info_tick(symbol).bid:
            price = mt5.symbol_info_tick(symbol).bid

        request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
        }   

    elif BoS == "BUY":
        if price > mt5.symbol_info_tick(symbol).ask:
            price = mt5.symbol_info_tick(symbol).ask

        request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
        } 


    else:
        request = None


     
    # send a trading request
    result = mt5.order_send(request)
    # check the execution result
    print("1. order_send(): {} {} at price {}, with lot {}, with deviation {}".format(BoS, symbol, price, lot, deviation))
    update.message.reply_text("1. order_send(): {} {} at price {}, with lot {}, with deviation {}".format(BoS, symbol, price, lot, deviation))

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        update.message.reply_text("2. order_send failed, retcode={}".format(result.retcode))

        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            update.message.reply_text("   {}={}".format(field,result_dict[field]))

            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
                    update.message.reply_text("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))

        # print("shutdown() and quit")
        # update.message.reply_text("shutdown() and quit")


    else: 
        print("2. order_send done, ", result)
        update.message.reply_text("2. order_send done, ".format(result))























def main():
    updater = Updater(botToken, use_context=True)
    dp = updater.dispatcher


    dp.add_handler(MessageHandler(Filters.text, catch_text))

   
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()