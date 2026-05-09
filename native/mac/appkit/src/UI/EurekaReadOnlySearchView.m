#import "EurekaReadOnlySearchView.h"

@interface EurekaReadOnlySearchView ()
@property (nonatomic, strong) NSTextView *textView;
@end

@implementation EurekaReadOnlySearchView

- (instancetype)initWithFrame:(NSRect)frameRect
{
    self = [super initWithFrame:frameRect];
    if (self) {
        self.textView = [[NSTextView alloc] initWithFrame:[self bounds]];
        [self.textView setEditable:NO];
        [self.textView setAutoresizingMask:(NSViewWidthSizable | NSViewHeightSizable)];
        [self addSubview:self.textView];
        [self setSummaryText:@"Eureka AppKit read-only fixture view"];
    }
    return self;
}

- (void)setSummaryText:(NSString *)summaryText
{
    NSString *blockedText;

    blockedText = @"\n\nBlocked actions: download, install, execute, emulate.\nNo rights, safety, installability, or truth acceptance claims.";
    [[self.textView textStorage] setAttributedString:[[NSAttributedString alloc] initWithString:[summaryText stringByAppendingString:blockedText]]];
}

@end
