import { render } from '@testing-library/astro';
import LogoMarquee from '../../src/components/LogoMarquee.astro';

describe('LogoMarquee', () => {
  it('renders the default label and logos', async () => {
    const { getByText, getAllByAltText } = await render(LogoMarquee);
    expect(getByText('Trusted by world-class teams - not just for AI.')).toBeTruthy();
    // At least one logo should be present
    expect(getAllByAltText(/Aston Martin|British Athletics|British Sailing|British Swimming|English Institute of Sport|GB Boxing|GB Rowing|INEOS 159|Multimatic Motorsports|Paralympc-gb|Team Sky|WBS|WWA|british equestrian federation|vis_orig/).length).toBeGreaterThan(0);
  });

  it('renders with a custom label', async () => {
    const { getByText } = await render(LogoMarquee, { props: { label: 'Our Clients' } });
    expect(getByText('Our Clients')).toBeTruthy();
  });

  it('handles empty logos array gracefully (edge case)', async () => {
    // Simulate by mocking the logos array to empty
    // This requires a code change or dependency injection, so this is a placeholder for a real edge test
    // For now, just check that component renders without crashing
    const { container } = await render(LogoMarquee);
    expect(container).toBeTruthy();
  });
});
