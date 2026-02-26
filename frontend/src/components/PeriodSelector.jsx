import { useState, useEffect } from 'react';
import {
  Box, Tabs, Tab, Select, MenuItem, FormControl, InputLabel,
  Typography, Chip, Paper,
} from '@mui/material';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import DateRangeIcon from '@mui/icons-material/DateRange';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import reportService from '../services/reportService';

function PeriodSelector({ onPeriodChange, initialPeriodType = 'daily' }) {
  const [periodType, setPeriodType] = useState(initialPeriodType);
  const [periods, setPeriods] = useState(null);
  const [selectedDaily, setSelectedDaily] = useState('');
  const [selectedWeekly, setSelectedWeekly] = useState('');
  const [selectedMonthly, setSelectedMonthly] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPeriods = async () => {
      try {
        const response = await reportService.getPeriods();
        setPeriods(response.data);

        if (response.data.daily?.length > 0) {
          setSelectedDaily(response.data.daily[0].date);
        }
        if (response.data.weekly?.length > 0) {
          const w = response.data.weekly[0];
          setSelectedWeekly(`${w.year}-${w.week}`);
        }
        if (response.data.monthly?.length > 0) {
          const m = response.data.monthly[0];
          setSelectedMonthly(`${m.year}-${m.month}`);
        }

        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch periods:', error);
        setLoading(false);
      }
    };

    fetchPeriods();
  }, []);

  useEffect(() => {
    if (!loading && periods) {
      handlePeriodSelect();
    }
  }, [loading, periodType]);

  const handleTabChange = (event, newValue) => {
    setPeriodType(newValue);
  };

  const handlePeriodSelect = () => {
    if (!periods) return;

    let params = { periodType };

    switch (periodType) {
      case 'daily':
        if (selectedDaily) {
          params.date = selectedDaily;
          const selected = periods.daily?.find((d) => d.date === selectedDaily);
          params.label = selected?.label || selectedDaily;
        }
        break;
      case 'weekly':
        if (selectedWeekly) {
          const [year, week] = selectedWeekly.split('-').map(Number);
          params.year = year;
          params.week = week;
          const selected = periods.weekly?.find((w) => w.year === year && w.week === week);
          params.label = selected?.label || `${year}년 ${week}주차`;
        }
        break;
      case 'monthly':
        if (selectedMonthly) {
          const [year, month] = selectedMonthly.split('-').map(Number);
          params.year = year;
          params.month = month;
          const selected = periods.monthly?.find((m) => m.year === year && m.month === month);
          params.label = selected?.label || `${year}년 ${month}월`;
        }
        break;
      default:
        break;
    }

    if (onPeriodChange) {
      onPeriodChange(params);
    }
  };

  useEffect(() => {
    if (!loading) {
      handlePeriodSelect();
    }
  }, [selectedDaily, selectedWeekly, selectedMonthly]);

  if (loading || !periods) {
    return <Box p={2}>로딩 중...</Box>;
  }

  return (
    <Paper sx={{ mb: 3 }}>
      <Tabs
        value={periodType}
        onChange={handleTabChange}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab value="daily" label="일별" icon={<CalendarTodayIcon />} iconPosition="start" />
        <Tab value="weekly" label="주별" icon={<DateRangeIcon />} iconPosition="start" />
        <Tab value="monthly" label="월별" icon={<CalendarMonthIcon />} iconPosition="start" />
      </Tabs>

      <Box sx={{ p: 2 }}>
        {periodType === 'daily' && (
          <FormControl fullWidth size="small">
            <InputLabel>날짜 선택</InputLabel>
            <Select
              value={selectedDaily}
              onChange={(e) => setSelectedDaily(e.target.value)}
              label="날짜 선택"
            >
              {periods.daily?.map((d) => (
                <MenuItem key={d.date} value={d.date}>
                  {d.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {periodType === 'weekly' && (
          <FormControl fullWidth size="small">
            <InputLabel>주차 선택</InputLabel>
            <Select
              value={selectedWeekly}
              onChange={(e) => setSelectedWeekly(e.target.value)}
              label="주차 선택"
            >
              {periods.weekly?.map((w) => (
                <MenuItem key={`${w.year}-${w.week}`} value={`${w.year}-${w.week}`}>
                  {w.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {periodType === 'monthly' && (
          <FormControl fullWidth size="small">
            <InputLabel>월 선택</InputLabel>
            <Select
              value={selectedMonthly}
              onChange={(e) => setSelectedMonthly(e.target.value)}
              label="월 선택"
            >
              {periods.monthly?.map((m) => (
                <MenuItem key={`${m.year}-${m.month}`} value={`${m.year}-${m.month}`}>
                  {m.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <Box mt={2} display="flex" alignItems="center" gap={1}>
          <Typography variant="body2" color="text.secondary">
            현재:
          </Typography>
          <Chip
            size="small"
            color="primary"
            label={
              periodType === 'daily'
                ? periods.daily?.find((d) => d.date === selectedDaily)?.label
                : periodType === 'weekly'
                  ? periods.weekly?.find((w) => `${w.year}-${w.week}` === selectedWeekly)?.label
                  : periods.monthly?.find((m) => `${m.year}-${m.month}` === selectedMonthly)?.label
            }
          />
        </Box>
      </Box>
    </Paper>
  );
}

export default PeriodSelector;
