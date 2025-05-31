import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def draw_candlestick(frame, df_graph, symbol, state):
    # state: dict, içinde canvas, ax, fig, saatler, bollinger_df, bollinger_visible
    # ...candlestick çizim kodu buraya taşınacak...
    # state['canvas'], state['ax'], state['fig'], state['saatler'], state['bollinger_df'], state['bollinger_visible'] güncellenmeli
    pass

def draw_macd(frame, df_graph, symbol, state):
    # state: dict, içinde canvas, ax, fig, saatler, bollinger_df, bollinger_visible
    # ...macd çizim kodu buraya taşınacak...
    pass

def toggle_bollinger(state):
    # state: dict, içinde ax, fig, canvas, bollinger_visible, saatler, bollinger_df
    # ...bollinger göster/gizle kodu buraya taşınacak...
    pass
