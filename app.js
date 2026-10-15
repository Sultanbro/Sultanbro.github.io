(() => {
  const tg = window.Telegram?.WebApp;
  const inTelegram = Boolean(tg?.initData);
  const status = document.getElementById('selection');
  const usercard = document.getElementById('usercard');
  const buttons = [...document.querySelectorAll('[data-item]')];
  let selected = '';

  if (inTelegram) {
    tg.ready();
    tg.expand();
    tg.MainButton.color = '#276449';
    tg.MainButton.textColor = '#ffffff';
    const user = tg.initDataUnsafe?.user;
    usercard.textContent = user ? `Здравствуйте, ${user.first_name || ''}!` : 'Каталог открыт в Telegram';
  } else {
    usercard.textContent = 'Предпросмотр каталога. Для оформления откройте его кнопкой бота в Telegram.';
  }

  buttons.forEach(button => button.addEventListener('click', () => {
    selected = selected === button.dataset.item ? '' : button.dataset.item;
    buttons.forEach(item => {
      const active = item.dataset.item === selected;
      item.setAttribute('aria-pressed', String(active));
      item.textContent = active ? 'Выбрано' : 'Выбрать';
    });
    status.textContent = selected ? `Выбран демо-набор ${selected}` : 'Выберите один набор из каталога';
    if (inTelegram) {
      if (selected) {
        tg.MainButton.setText(`Оформить набор ${selected}`);
        tg.MainButton.show();
      } else tg.MainButton.hide();
    }
  }));
  if (inTelegram) tg.onEvent('mainButtonClicked', () => {
    if (selected) tg.sendData(selected);
  });
})();
