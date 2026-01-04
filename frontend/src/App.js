import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Switch,
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Button,
  TextField,
  InputAdornment,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import {
  Search as SearchIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  SportsEsports as GamesIcon,
  Apps as AppsIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const App = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [user, setUser] = useState(null);
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [lastViewed, setLastViewed] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
    },
  });

  useEffect(() => {
    // Инициализация Telegram Web App
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      
      const initData = tg.initData;
      if (initData) {
        const params = new URLSearchParams(initData);
        const userData = JSON.parse(params.get('user') || '{}');
        setUser({
          id: userData.id,
          username: userData.username,
          first_name: userData.first_name,
          last_name: userData.last_name
        });
        
        // Загрузка данных
        loadData(userData.id);
      }
    }
  }, []);

  const loadData = async (telegramId) => {
    try {
      const token = btoa(telegramId.toString());
      const headers = { Authorization: `Bearer ${token}` };
      
      const [catsRes, prodsRes] = await Promise.all([
        axios.get(`${API_URL}/categories/`, { headers }),
        axios.get(`${API_URL}/products/`, { headers })
      ]);
      
      setCategories(catsRes.data);
      setProducts(prodsRes.data);
      
      // Загрузка последнего просмотренного
      // Здесь должна быть дополнительная логика
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleBuy = (product) => {
    // Логика покупки
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.showPopup({
        title: 'Выберите способ оплаты',
        message: `Товар: ${product.name}\nЦена: ${product.price}`,
        buttons: [
          { id: 'usdt', type: 'default', text: 'USDT' },
          { id: 'ton', type: 'default', text: 'TON' },
          { id: 'rub', type: 'default', text: 'Рубли' },
          { id: 'cancel', type: 'cancel' }
        ]
      }, (btnId) => {
        if (btnId !== 'cancel') {
          processPayment(product, btnId);
        }
      });
    }
  };

  const processPayment = async (product, method) => {
    try {
      const token = btoa(user.id.toString());
      const response = await axios.post(`${API_URL}/orders/`, {
        product_id: product.id,
        payment_method: method
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Дальнейшая логика оплаты...
    } catch (error) {
      console.error('Error creating order:', error);
    }
  };

  const gameCategories = categories.filter(cat => cat.is_game);
  const appCategories = categories.filter(cat => !cat.is_game);

  const filteredProducts = searchQuery
    ? products.filter(p => 
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : products;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              UNIVERSAL SHOP
            </Typography>
            <IconButton color="inherit">
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
            <Switch
              checked={darkMode}
              onChange={(e) => setDarkMode(e.target.checked)}
            />
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ mt: 3 }}>
          {/* Поиск */}
          <TextField
            fullWidth
            placeholder="Поиск товаров..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ mb: 3 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          {/* Блок Игры */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              <GamesIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Игры
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              {gameCategories.map((category) => (
                <Grid item key={category.id}>
                  <Button
                    variant="outlined"
                    startIcon={category.emoji ? <span>{category.emoji}</span> : <GamesIcon />}
                  >
                    {category.name}
                  </Button>
                </Grid>
              ))}
            </Grid>
            <Button variant="text" size="small">Смотреть все</Button>
          </Box>

          {/* Блок Приложения */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              <AppsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Приложения
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              {appCategories.map((category) => (
                <Grid item key={category.id}>
                  <Button
                    variant="outlined"
                    startIcon={category.emoji ? <span>{category.emoji}</span> : <AppsIcon />}
                  >
                    {category.name}
                  </Button>
                </Grid>
              ))}
            </Grid>
            <Button variant="text" size="small">Смотреть все</Button>
          </Box>

          {/* Последний просмотренный */}
          {lastViewed && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Смотрел в последний раз
              </Typography>
              <Card>
                <CardContent>
                  <Typography variant="h6">{lastViewed.name}</Typography>
                  <Typography color="textSecondary">{lastViewed.description}</Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">Купить</Button>
                  <Button size="small" color="secondary">Удалить</Button>
                </CardActions>
              </Card>
            </Box>
          )}

          {/* Все товары */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Все товары
            </Typography>
            <Grid container spacing={3}>
              {filteredProducts.map((product) => (
                <Grid item xs={12} sm={6} md={4} key={product.id}>
                  <Card>
                    {product.image_url && (
                      <CardMedia
                        component="img"
                        height="200"
                        image={product.image_url}
                        alt={product.name}
                      />
                    )}
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {product.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" paragraph>
                        {product.description}
                      </Typography>
                      <Typography variant="h6" color="primary">
                        ${product.price}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        color="primary"
                        onClick={() => handleBuy(product)}
                      >
                        Купить
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;
