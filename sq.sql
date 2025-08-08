WITH post_stats AS (
  SELECT 
    post_id,
    post_date,
    likes_count,
    -- Час публикации (0-23)
    CAST(strftime('%H', post_date) AS INTEGER) AS post_hour,
    -- День недели (0-6, где 0=воскресенье)
    CAST(strftime('%w', post_date) AS INTEGER) AS day_of_week,
    -- Дней между постами (для перевода в месяцы)
    (julianday(post_date) - julianday(LAG(post_date, 1) OVER (ORDER BY post_date))) AS days_between_posts
  FROM vk_posts
)

SELECT 
  factor,
  value,
  ROUND(avg_likes, 1) AS avg_likes,
  posts_count,
  impact_rank
FROM (
  -- Анализ по часам
  SELECT 
    'hour' AS factor,
    post_hour || ':00' AS value,
    AVG(likes_count) AS avg_likes,
    COUNT(*) AS posts_count,
    RANK() OVER (ORDER BY AVG(likes_count) DESC) AS impact_rank
  FROM post_stats
  GROUP BY post_hour

  UNION ALL

  -- Анализ по дням недели
  SELECT 
    'day_of_week' AS factor,
    CASE day_of_week
      WHEN 0 THEN 'Воскресенье'
      WHEN 1 THEN 'Понедельник'
      WHEN 2 THEN 'Вторник'
      WHEN 3 THEN 'Среда'
      WHEN 4 THEN 'Четверг'
      WHEN 5 THEN 'Пятница'
      WHEN 6 THEN 'Суббота'
    END AS value,
    AVG(likes_count) AS avg_likes,
    COUNT(*) AS posts_count,
    RANK() OVER (ORDER BY AVG(likes_count) DESC) AS impact_rank
  FROM post_stats
  GROUP BY day_of_week

  UNION ALL

  -- Анализ по интервалам между постами (в месяцах)
  SELECT 
    'months_between_posts' AS factor,
    CASE 
      WHEN days_between_posts IS NULL THEN 'Первый пост'
      WHEN days_between_posts/30 < 1 THEN 'Менее 1 месяца'
      WHEN days_between_posts/30 BETWEEN 1 AND 5 THEN '1-5 месяцев'
      ELSE 'Более 5 месяцев'
    END AS value,
    AVG(likes_count) AS avg_likes,
    COUNT(*) AS posts_count,
    RANK() OVER (ORDER BY AVG(likes_count) DESC) AS impact_rank
  FROM post_stats
  GROUP BY 
    CASE 
      WHEN days_between_posts IS NULL THEN 0
      WHEN days_between_posts/30 < 1 THEN 1
      WHEN days_between_posts/30 BETWEEN 1 AND 5 THEN 2
      ELSE 3
    END
)
ORDER BY impact_rank, factor;

