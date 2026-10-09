// k6/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

// 테스트 옵션 설정
export const options = {
    stages: [
        { duration: '10s', target: 5 },  // 10초 동안 가상 사용자(VU)를 5명으로 증가
        { duration: '20s', target: 5 },  // 20초 동안 5명 유지 (부하 유지)
        { duration: '10s', target: 0 },  // 10초 동안 0명으로 감소 (종료)
    ],
    thresholds: {
        // 성공률이 95% 이상이어야 함
        http_req_failed: ['rate<0.05'], 
        // 95%의 요청이 5초(5000ms) 이내에 처리되어야 함 (LLM 응답 시간 고려)
        http_req_duration: ['p(95)<5000'], 
    },
};

const BASE_URL = 'http://127.0.0.1:8000';

export default function () {
    // 1. Health Check (서버 자체 성능 검증)
    let resHealth = http.get(`${BASE_URL}/health`);
    check(resHealth, {
        'health check status is 200': (r) => r.status === 200,
    });

    // 2. AI 요리사 API (실제 LLM 연동 성능 검증)
    const payload = JSON.stringify({
        ingredients: '계란, 파, 양파, 굴소스'
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let resRecipe = http.post(`${BASE_URL}/api/v1/recipe`, payload, params);
    
    // 상태 코드가 200인지, 또는 Rate Limit(429)나 타임아웃(502)이 났는지 체크
    check(resRecipe, {
        'recipe API status is 200': (r) => r.status === 200,
        // 운영 관점: 외부 API 제한에 걸렸는지 확인하는 지표
        'is not rate limited (429)': (r) => r.status !== 429, 
    });

    // 다음 요청 전 1~2초 대기 (실제 사용자의 행동 모사 및 Rate Limit 방지)
    sleep(Math.random() * 1 + 1);
}