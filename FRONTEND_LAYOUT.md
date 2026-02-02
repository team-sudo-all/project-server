# 🏥 병원 추천 페이지 프론트엔드 레이아웃

## 📌 개요
- **기능**: 사용자 위치 기반 병원 추천 + 카카오맵 연동
- **UI 방식**: 핀 클릭 시 반투명 오버레이 + 모달 팝업
- **기술 스택**: React + Tailwind CSS + 카카오맵 API

---

## 🗺️ 화면 구조

### 기본 상태
```
┌─────────────────────────────────────────┐
│ 📱 Header: AI 분석 결과                 │
│ 추천 진료과: 소화기내과 | 응급도: High  │
├─────────────────────────────────────────┤
│                                          │
│          🗺️ 카카오맵 (전체 화면)        │
│                                          │
│   📍 (병원 마커들)                       │
│   📍                                     │
│        📍                                │
│             📍 ← 클릭!                   │
│                  📍                      │
│                                          │
│         🔴 (내 위치)                     │
│                                          │
└─────────────────────────────────────────┘
```

### 핀 클릭 시 (모달 열림)
```
┌─────────────────────────────────────────┐
│  Header (AI 분석)                       │
├─────────────────────────────────────────┤
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 지도가 어둡게 보임
│ ░░ 🗺️ (어두운 지도 + 블러)  ░░░░░░░░░ │
│ ░░     ┌─────────────────┐      ░░░░░░ │
│ ░░     │ (병원 이름)      │ ×   ░░░░░░ │
│ ░░     │                  │      ░░░░░░ │
│ ░░     │ Clinic Hours:    │      ░░░░░░ │
│ ░░     │ Mon-Sat 10-18    │      ░░░░░░ │
│ ░░     │ [상세 정보]      │      ░░░░░░ │
│ ░░     │                  │      ░░░░░░ │
│ ░░     │ [전화] [길찾기]  │      ░░░░░░ │
│ ░░     └─────────────────┘      ░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────┘
```

---

## 📁 컴포넌트 구조

```
src/
├── pages/
│   └── HospitalRecommendation.jsx    # 메인 페이지
├── components/
│   ├── AIAnalysisHeader.jsx          # AI 분석 결과 헤더
│   ├── KakaoMap.jsx                  # 카카오맵
│   └── HospitalDetailModal.jsx       # 병원 상세 모달
└── styles/
    └── animations.css                # 애니메이션 CSS
```

---

## 📄 컴포넌트 코드

### 1. 메인 페이지 (HospitalRecommendation.jsx)

```jsx
import React, { useState, useEffect } from 'react';
import AIAnalysisHeader from '../components/AIAnalysisHeader';
import KakaoMap from '../components/KakaoMap';
import HospitalDetailModal from '../components/HospitalDetailModal';

function HospitalRecommendation() {
  const [recommendations, setRecommendations] = useState(null);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [loading, setLoading] = useState(false);

  // 사용자 위치 가져오기
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => {
        console.error('위치 정보를 가져올 수 없습니다:', error);
        // 기본 위치 (서울 시청)
        setUserLocation({
          latitude: 37.5665,
          longitude: 126.9780
        });
      }
    );
  }, []);

  // 병원 추천 API 호출
  const searchHospitals = async (symptoms) => {
    if (!userLocation) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/recommend-hospitals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "gildong123", // 실제 로그인된 사용자 ID로 교체
          symptoms: symptoms,
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
          radius: 2000
        })
      });
      
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('병원 검색 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 모달 열릴 때 스크롤 방지
  useEffect(() => {
    if (selectedHospital) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [selectedHospital]);

  return (
    <div className="h-screen flex flex-col relative">
      {/* AI 분석 결과 헤더 */}
      <AIAnalysisHeader data={recommendations} />
      
      {/* 지도 영역 (전체 화면) */}
      <div className="flex-1 relative">
        <KakaoMap 
          hospitals={recommendations?.hospitals}
          userLocation={userLocation}
          onMarkerClick={setSelectedHospital}
        />
        
        {/* 로딩 표시 */}
        {loading && (
          <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          </div>
        )}
      </div>
      
      {/* 병원 상세 모달 (핀 클릭 시) */}
      {selectedHospital && (
        <HospitalDetailModal 
          hospital={selectedHospital}
          onClose={() => setSelectedHospital(null)}
        />
      )}
    </div>
  );
}

export default HospitalRecommendation;
```

---

### 2. AI 분석 헤더 (AIAnalysisHeader.jsx)

```jsx
import React from 'react';

function AIAnalysisHeader({ data }) {
  if (!data) {
    return (
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 shadow-lg">
        <div className="flex items-center justify-center gap-2">
          <span className="text-2xl">🏥</span>
          <span>증상을 입력하면 병원을 추천해드립니다</span>
        </div>
      </div>
    );
  }

  const urgencyColor = {
    'Emergency': 'bg-red-500',
    'High': 'bg-orange-500',
    'Moderate': 'bg-yellow-500',
    'Low': 'bg-green-500'
  };

  return (
    <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 shadow-lg">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* 추천 진료과 */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏥</span>
          <div>
            <div className="text-sm opacity-90">추천 진료과</div>
            <div className="font-bold text-lg">{data.recommended_department}</div>
          </div>
        </div>
        
        {/* 응급도 */}
        <span className={`px-4 py-2 rounded-full text-sm font-medium shadow-md ${urgencyColor[data.urgency_level] || 'bg-gray-500'}`}>
          {data.urgency_level}
        </span>
      </div>
      
      {/* 추천 이유 */}
      <p className="text-xs opacity-80 mt-2 text-center max-w-xl mx-auto">
        💡 {data.reason}
      </p>
    </div>
  );
}

export default AIAnalysisHeader;
```

---

### 3. 카카오맵 (KakaoMap.jsx)

```jsx
import React, { useEffect, useRef } from 'react';

function KakaoMap({ hospitals, userLocation, onMarkerClick }) {
  const mapRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // 카카오맵 SDK 로드 확인
    if (!window.kakao || !window.kakao.maps) {
      console.error('카카오맵 SDK가 로드되지 않았습니다.');
      return;
    }
    
    if (!userLocation) return;

    const container = document.getElementById('kakao-map');
    const options = {
      center: new window.kakao.maps.LatLng(
        userLocation.latitude, 
        userLocation.longitude
      ),
      level: 5 // 줌 레벨
    };
    
    const map = new window.kakao.maps.Map(container, options);
    mapRef.current = map;

    // 지도 컨트롤 추가
    const zoomControl = new window.kakao.maps.ZoomControl();
    map.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);

    // 내 위치 마커 (빨간색 별 아이콘)
    const myPosition = new window.kakao.maps.LatLng(
      userLocation.latitude, 
      userLocation.longitude
    );
    
    const myMarkerImage = new window.kakao.maps.MarkerImage(
      'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
      new window.kakao.maps.Size(24, 35)
    );
    
    const myMarker = new window.kakao.maps.Marker({
      position: myPosition,
      image: myMarkerImage,
      title: '내 위치'
    });
    myMarker.setMap(map);

    // 내 위치 인포윈도우
    const myInfoWindow = new window.kakao.maps.InfoWindow({
      content: '<div style="padding:5px;font-size:12px;">📍 내 위치</div>'
    });
    
    window.kakao.maps.event.addListener(myMarker, 'click', () => {
      myInfoWindow.open(map, myMarker);
    });

  }, [userLocation]);

  // 병원 마커 업데이트
  useEffect(() => {
    if (!mapRef.current || !hospitals) return;

    const map = mapRef.current;

    // 기존 병원 마커 제거
    markersRef.current.forEach(({ marker }) => {
      marker.setMap(null);
    });
    markersRef.current = [];

    // 새 병원 마커 생성
    hospitals.forEach((hospital, index) => {
      const position = new window.kakao.maps.LatLng(hospital.y, hospital.x);
      
      const marker = new window.kakao.maps.Marker({
        position: position,
        title: hospital.name
      });
      marker.setMap(map);

      // 마커 클릭 이벤트
      window.kakao.maps.event.addListener(marker, 'click', () => {
        onMarkerClick(hospital);
        
        // 클릭한 마커를 지도 중심으로 부드럽게 이동
        map.panTo(position);
      });

      markersRef.current.push({ marker, hospital });
    });

    // 모든 마커가 보이도록 지도 범위 조정 (옵션)
    if (hospitals.length > 0) {
      const bounds = new window.kakao.maps.LatLngBounds();
      
      // 내 위치 포함
      if (userLocation) {
        bounds.extend(new window.kakao.maps.LatLng(
          userLocation.latitude, 
          userLocation.longitude
        ));
      }
      
      // 병원 위치 포함
      hospitals.forEach((hospital) => {
        bounds.extend(new window.kakao.maps.LatLng(hospital.y, hospital.x));
      });
      
      map.setBounds(bounds);
    }

  }, [hospitals, onMarkerClick]);

  return (
    <div 
      id="kakao-map" 
      className="w-full h-full"
      style={{ minHeight: '400px' }}
    />
  );
}

export default KakaoMap;
```

---

### 4. 병원 상세 모달 (HospitalDetailModal.jsx) ⭐

```jsx
import React, { useEffect } from 'react';

function HospitalDetailModal({ hospital, onClose }) {
  // ESC 키로 모달 닫기
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // 배경(지도) 클릭 시 닫기
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <>
      {/* 반투명 오버레이 (지도가 어둡게 보임) */}
      <div 
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[2px] animate-fadeIn"
        onClick={handleBackdropClick}
      />
      
      {/* 모달 컨테이너 */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div 
          className="bg-white rounded-2xl shadow-2xl max-w-lg w-full pointer-events-auto animate-slideUp"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 (노란색 배경) */}
          <div className="bg-yellow-50 rounded-t-2xl p-6 border-b-2 border-yellow-200">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-800 mb-1">
                  {hospital.name}
                </h2>
                <p className="text-sm text-gray-500">{hospital.department}</p>
              </div>
              {/* 닫기 버튼 */}
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors ml-4 p-1"
                aria-label="닫기"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* 본문 */}
          <div className="p-6">
            {/* 진료 시간 */}
            <div className="mb-6 text-center">
              <p className="text-gray-600 text-sm">
                🕐 Clinic Hours: Mon-Sat, 10:00 - 18:00
              </p>
            </div>

            {/* 상세 정보 박스 */}
            <div className="bg-gray-50 rounded-xl p-5 mb-6 space-y-4">
              {/* 거리 및 진료과 */}
              <div className="flex items-start gap-3">
                <span className="text-blue-500 text-xl flex-shrink-0">📍</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-500 mb-1">위치 및 진료과</div>
                  <div className="font-medium text-gray-800">
                    {hospital.distance} | {hospital.department}
                  </div>
                </div>
              </div>

              {/* 전화번호 */}
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl flex-shrink-0">📞</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-500 mb-1">전화번호</div>
                  <div className="font-medium text-gray-800">
                    {hospital.phone || '정보 없음'}
                  </div>
                </div>
              </div>

              {/* 주소 */}
              <div className="flex items-start gap-3">
                <span className="text-orange-500 text-xl flex-shrink-0">📌</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-500 mb-1">주소</div>
                  <div className="text-sm text-gray-700">
                    {hospital.address}
                  </div>
                </div>
              </div>
            </div>

            {/* 액션 버튼 */}
            <div className="grid grid-cols-2 gap-3">
              {/* 전화하기 버튼 */}
              <button 
                className="bg-green-500 hover:bg-green-600 text-white py-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl active:scale-95"
                onClick={() => {
                  if (hospital.phone) {
                    window.location.href = `tel:${hospital.phone}`;
                  } else {
                    alert('전화번호 정보가 없습니다.');
                  }
                }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                전화하기
              </button>
              
              {/* 길찾기 버튼 */}
              <button 
                className="bg-blue-500 hover:bg-blue-600 text-white py-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl active:scale-95"
                onClick={() => {
                  if (hospital.url) {
                    window.open(hospital.url, '_blank');
                  } else {
                    // 카카오맵 웹으로 직접 이동
                    const kakaoMapUrl = `https://map.kakao.com/link/map/${hospital.name},${hospital.y},${hospital.x}`;
                    window.open(kakaoMapUrl, '_blank');
                  }
                }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                길찾기
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default HospitalDetailModal;
```

---

## 🎨 CSS 애니메이션 (animations.css)

```css
/* 페이드인 애니메이션 (오버레이) */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fadeIn {
  animation: fadeIn 0.2s ease-out;
}

/* 슬라이드업 + 스케일 애니메이션 (모달) */
@keyframes slideUp {
  from {
    transform: translateY(30px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.animate-slideUp {
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 반투명 배경 */
.bg-black\/50 {
  background-color: rgba(0, 0, 0, 0.5);
}

/* 배경 블러 효과 */
.backdrop-blur-\[2px\] {
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}
```

---

## ⚙️ Tailwind CSS 설정 (선택사항)

Tailwind 사용 시 `tailwind.config.js`에 애니메이션 추가:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        fadeIn: 'fadeIn 0.2s ease-out',
        slideUp: 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(30px) scale(0.95)', opacity: '0' },
          '100%': { transform: 'translateY(0) scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

---

## 🔧 카카오맵 SDK 설정

### 1. public/index.html에 추가

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>병원 추천</title>
  
  <!-- 카카오맵 SDK -->
  <script 
    type="text/javascript" 
    src="//dapi.kakao.com/v2/maps/sdk.js?appkey=YOUR_JAVASCRIPT_KEY&libraries=services"
  ></script>
</head>
<body>
  <div id="root"></div>
</body>
</html>
```

### 2. 카카오 JavaScript 키
- **카카오 개발자 콘솔**: https://developers.kakao.com
- **JavaScript 키**: `b6e324b792e7c792f50840a25d79290a`

```html
<script src="//dapi.kakao.com/v2/maps/sdk.js?appkey=b6e324b792e7c792f50840a25d79290a&libraries=services"></script>
```

---

## 📱 API 연동 흐름

```
[사용자 흐름]

1. 페이지 로드
   ├─ 위치 권한 요청
   └─ 사용자 위치 획득 (GPS)

2. 증상 입력 후 검색 버튼 클릭
   └─ POST /api/recommend-hospitals 호출
      {
        "user_id": "gildong123",
        "symptoms": "배가 아파요",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "radius": 2000
      }

3. API 응답 수신
   └─ 지도에 병원 마커 표시

4. 사용자가 병원 마커(📍) 클릭
   └─ 모달 열림 (지도 어두워짐)

5. 모달에서 액션
   ├─ [전화하기] → tel:전화번호 호출
   ├─ [길찾기] → 카카오맵 URL 열기
   └─ [×] 또는 배경 클릭 → 모달 닫힘
```

---

## 📋 API Response 예시

### /api/recommend-hospitals 응답

```json
{
  "recommended_department": "소화기내과",
  "urgency_level": "High",
  "reason": "복통과 구토 증상은 소화기 문제일 가능성이 높습니다.",
  "hospitals": [
    {
      "name": "서울아산병원",
      "department": "소화기내과",
      "distance": "850m",
      "address": "서울시 송파구 올림픽로 43길 88",
      "phone": "02-3010-3114",
      "url": "http://place.map.kakao.com/12345",
      "x": 127.0856,
      "y": 37.5267
    },
    {
      "name": "삼성서울병원",
      "department": "소화기내과", 
      "distance": "1200m",
      "address": "서울시 강남구 일원로 81",
      "phone": "02-3410-2114",
      "url": "http://place.map.kakao.com/67890",
      "x": 127.0889,
      "y": 37.4881
    }
  ]
}
```

---

## ✅ 체크리스트

- [ ] React 프로젝트 생성 (`npx create-react-app`)
- [ ] Tailwind CSS 설치 및 설정
- [ ] 카카오맵 SDK 추가 (JavaScript 키)
- [ ] 컴포넌트 파일 생성
- [ ] API 연동 테스트
- [ ] 모바일 반응형 확인
- [ ] 에러 핸들링 추가

---

## 📞 문의

- **백엔드 API 문서**: API_DOCUMENTATION.md
- **백엔드 서버**: http://127.0.0.1:8000
- **최종 업데이트**: 2026-01-30
